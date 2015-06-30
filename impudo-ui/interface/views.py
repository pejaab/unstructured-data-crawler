from django.core.exceptions import ValidationError
from django.http import HttpResponse
from django.shortcuts import redirect, render

from interface.forms import TemplateForm
from interface.models import Template

def home_page(request):
    return render(request, 'home.html', {'form': TemplateForm()})

def view_template(request, template_id):
    item = Template.objects.get(id=template_id)
    form = TemplateForm()
    if request.method == 'POST':
        form = TemplateForm(data=request.POST, instance=item)
        if form.is_valid():
            item = form.save()
            form.analyze()
            return redirect(item)  
        else:
            return render(request, 'template.html', {'form': form, 'item': item}) 
    return render(
            request, 'template.html', {
                'item': item, 
                'form': TemplateForm(initial={'url': item.url, 'desc': item.desc})
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
