import random

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse 
from django import forms
from markdown import markdown
from . import util


class NewPageForm(forms.Form):
    title = forms.CharField(label="", widget=forms.TextInput(attrs={'class':'form-control'}))
    markdown_content = forms.CharField(label="", widget=forms.Textarea(attrs={'class' : 'form-control'}))

class EditPageForm(forms.Form):
    new_content = forms.CharField(label="", widget=forms.Textarea(attrs={'class' : 'form-control'}))


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })
    

def display_entry(request, entry_title):
    # check if entry exist or not
    markdown_content = util.get_entry(entry_title.capitalize())
    if not markdown_content:
        return HttpResponse("Page Not Found") 

    # conver entry to html and render
    html_content = markdown(markdown_content)
    return render(request, "encyclopedia/entry.html", {
        "entry_title": entry_title,
        "entry_content": html_content
    })

def search_entry(request):
    # get search query and start find entry 
    query = request.GET.get("q")
    markdown_content = util.get_entry(query.capitalize()) 

    filtered_entries = []
    if not markdown_content:
        # not found entry check all possible matches
        for entry in util.list_entries():
            # if found matches render entries that matches if not inform with message
            if query.lower() in entry.lower():
                filtered_entries.append(entry)
        return render(request, "encyclopedia/searched_entries.html", {
            "filtered_entries": filtered_entries, 
        })
    else:
        # found render redirect to entry page
        return HttpResponseRedirect(reverse('encyclopedia:entry_url', args=[query]))

def new_page(request):
    if request.method == 'POST':
        # take form data and save it as a form
        form = NewPageForm(request.POST)

        # if form data is valid (server side)
        if form.is_valid():
            # take form title and check if it exist as entry
            entry_title = form.cleaned_data["title"]
            
            # if already exist return error 
            if util.get_entry(entry_title.capitalize()):
                return render(request, 'encyclopedia/new_page.html', {
                    "form": form,
                    "error": "Entry with this name already exist"
                })
            
            # if not exist save entry to disk and redirect to entry page info
            markdown_content = form.cleaned_data["markdown_content"]         
            util.save_entry(entry_title, markdown_content)

            return HttpResponseRedirect(reverse('encyclopedia:entry_url', args=[entry_title]))
        # if not valid form render same page with error
        else:
            return render(request, 'encyclopedia/new_page.html', {
                    "form": form,
                    "error": "Invalid form data"
                })
    return render(request, "encyclopedia/new_page.html", {
        "form": NewPageForm()
    })


def edit_content(request, entry_title):
    
    if request.method == "POST":
        # store request data in form 
        form = EditPageForm(request.POST)
        # if valid data
        if form.is_valid():
            # get new entry content from request and replace it with old content and redirect
            new_content = form.cleaned_data["new_content"]
            util.save_entry(entry_title.lower().capitalize(), new_content)

            return HttpResponseRedirect(reverse('encyclopedia:entry_url', args=[entry_title]))
        else:
            # if not valid data rerender with error message
            return render(request, 'encyclopedia/edit.html', {
                "form": form
            })
    
    # get entry content
    entry_content = util.get_entry(entry_title.lower().capitalize())
    
    # add this content to form as inital value and render it to text area
    form = EditPageForm(initial={"new_content": entry_content})
    
    # return HttpResponse(f"hello {form}")
    return render(request, "encyclopedia/edit.html", {
        "entry_title": entry_title,
        "form": form
    })


def random_page(request):
    # get random title from entries and redirect to random entry page 
    entry_list = util.list_entries()
    random_element = random.choice(entry_list)
    return HttpResponseRedirect(reverse('encyclopedia:random_entry', args=[random_element]))

def random_entry(request, random_element):
    # get content of selected random entry convert it to html and render
    random_entry_markdown = util.get_entry(random_element)
    random_element_html = markdown(random_entry_markdown)
    
    return render(request, 'encyclopedia/entry.html', {
        "entry_title": random_element,
        "entry_content": random_element_html
    })