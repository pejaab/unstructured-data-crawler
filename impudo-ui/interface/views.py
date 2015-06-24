import re

from django.core.exceptions import ValidationError
from django.http import HttpResponse
from django.shortcuts import redirect, render

from interface.forms import TemplateItemForm
from interface.models import TemplateItem

def home_page(request):
    return render(request, 'home.html', {'form': TemplateItemForm()})

def view_template(request, template_id):
    item = TemplateItem.objects.get(id=template_id)
    form = TemplateItemForm()
    if request.method == 'POST':
        form = TemplateItemForm(data=request.POST, instance=item)
        if form.is_valid():
            item = form.save()
            return redirect(item)  
        else:
            return render(request, 'template.html', {'item': item, 'form': form}) 
    return render(
            request, 'template.html', {
                'item': item, 
                'form': TemplateItemForm(initial={'url': item.url, 'desc': item.desc})
                }
            )

def new_template(request):
    form = TemplateItemForm(data=request.POST)
    if form.is_valid():
        item = form.save()
        return redirect(item)
    else:
        return render(request, 'home.html', {'form': form})
