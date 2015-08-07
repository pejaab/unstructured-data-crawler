from django.core.exceptions import ValidationError
from django.http import HttpResponse
from django.shortcuts import redirect, render

from interface.forms import TemplateForm
from interface.models import Template, Crawler

def home_page(request):
    return render(request, 'home.html', {'form': TemplateForm()})

def view_template(request, template_id):
    item = Template.objects.get(id=template_id)
    form = TemplateForm()
    if request.method == 'POST':
        form = TemplateForm(data=request.POST, instance=item)
        if form.is_valid(): 
            print(request.POST)
            if 'dispatch' in request.POST:
                #TODO: start crawler & redirect to manage page
                if not 'record' in request.POST:
                    #TODO: error that no xpath was selected and return to same page content
                    return render(request, 'template.html', {'form': form, 'item': item,})
                # Activate selected records
                for record_id in request.POST.getlist('record'):
                    record = Crawler.objects.get(id=int(record_id))
                    record.save()
                #TODO: return to manage page
                # Only active records are kept in database 
                Crawler.objects.filter(template_id=template_id, active=0).delete() 
                return render(request, 'home.html', {'form': TemplateForm()})
            # Delete xpath records before re-searching them
            Crawler.objects.filter(template_id=template_id).delete()
            item = form.save()
            form.analyze()
            return redirect(item)  
        else:
            return render(request, 'template.html', {'form': form, 'item': item,}) 
    return render(
            request, 'template.html', {
                'item': item, 
                'form': TemplateForm(initial={'url': item.url, 'desc': item.desc}),
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
