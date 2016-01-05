from django.core.exceptions import ValidationError
from django.http import HttpResponse
from django.shortcuts import redirect, render

from interface.forms import TemplateForm
from interface.models import Template, Crawler, CrawlerImgPath
from interface.tasks import scrape

NO_SELECTION_ERROR = 'You need to select at least one option'

def home_page(request):
    return render(request, 'home.html', {'form': TemplateForm()})

def view_template(request, template_id):
    item = Template.objects.get(id=template_id)
    form = TemplateForm()
    if request.method == 'POST':
        form = TemplateForm(data=request.POST, instance=item)
        if form.is_valid():
            # Activate selected records
            for record_id in request.POST.getlist('record'):
                record = Crawler.objects.get(id=int(record_id))
                record.active = 1
                record.save()
            for img_id in request.POST.getlist('img'):
                img = CrawlerImgPath.objects.get(id=int(img_id))
                img.active = 1
                img.save()
            # Only inactive records are kept in database
            active_paths = list(Crawler.objects.filter(template_id=template_id, active=1))
            active_imgs = list(CrawlerImgPath.objects.filter(template_id=template_id, active=1))
            Crawler.objects.filter(template_id=template_id).delete()
            CrawlerImgPath.objects.filter(template_id=template_id).delete()
            form.save_active_paths(active_paths)
            form.save_active_imgs(active_imgs)

            if 'dispatch' in request.POST:
                #TODO: redirect to manage page
                if not 'record' in request.POST:
                    return render(request, 'template.html',
                        {'form': form, 'item': item,
                         'not_selected_error': NO_SELECTION_ERROR})
                else:
                    scrape.delay(template_id)
                    return render(request, 'home.html', {'form': TemplateForm()})

            # Delete xpath records before re-searching them
            Crawler.objects.filter(template_id=template_id).delete()
            CrawlerImgPath.objects.filter(template_id=template_id).delete()
            item = form.save()
            #TODO: which exceptions do I need?
            #try:
            form.analyze()
            return redirect(item)
            #except:
                #return render(request, '404.html')
        else:
            return render(request, 'template.html', {'form': form, 'item': item,})
    else:
        return render(
                request, 'template.html', {
                    'item': item,
                    'form': TemplateForm(initial={
                        'url': item.url, 'desc': item.desc, }),
                    }
                )

def new_template(request):
    form = TemplateForm(data=request.POST)
    if form.is_valid():
        item = form.save()
        form.analyze()
        return redirect(item)
    else:
        return render(request, 'home.html', {'form': form})
