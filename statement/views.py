from django.shortcuts import render
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404

from .models import Statement, DecisionTree
from .forms import StatementForm, DecisionTreeForm

# Create your views here.
def tree_view(
    request,
    tree_id
):

    tree = get_object_or_404(
        DecisionTree,
        pk=tree_id
    )

    roots = Statement.objects.filter(
        tree=tree,
        parent__isnull=True
    )

    return render(
        request,
        "statements/tree.html",
        {
            "tree": tree,
            "roots": roots
        }
    )


def statement_create(request):

    initial = {}

    tree = None

    tree_id = request.GET.get("tree")
    parent_id = request.GET.get("parent")

    if parent_id:

        parent = get_object_or_404(
            Statement,
            pk=parent_id
        )

        tree = parent.tree

        initial["parent"] = parent.id
        initial["tree"] = tree.id

    elif tree_id:

        tree = get_object_or_404(
            DecisionTree,
            pk=tree_id
        )

        initial["tree"] = tree.id

    if request.method == "POST":

        form = StatementForm(request.POST)

        if form.is_valid():

            statement = form.save()

            return redirect(
                "statements:tree_view",
                tree_id=statement.tree.id
            )

    else:

        form = StatementForm(initial=initial)

    return render(
        request,
        "statements/form.html",
        {
            "form": form,
            "title": "Create Node",
            "tree": tree,
        }
    )

def statement_update(
    request,
    pk
):

    statement = get_object_or_404(
        Statement,
        pk=pk
    )

    tree = statement.tree

    if request.method == "POST":

        form = StatementForm(
            request.POST,
            instance=statement
        )

        if form.is_valid():

            statement = form.save()

            return redirect(
                "statements:tree_view",
                tree_id=statement.tree.id
            )

    else:

        form = StatementForm(
            instance=statement
        )

    return render(
        request,
        "statements/form.html",
        {
            "form": form,
            "title": "Update Node",
            "tree": tree,
        }
    )

def statement_delete(
    request,
    pk
):

    statement = get_object_or_404(
        Statement,
        pk=pk
    )

    tree_id = statement.tree.id

    if request.method == "POST":

        statement.delete()

        return redirect(
            "statements:tree_view",
            tree_id=tree_id
        )

    return render(
        request,
        "statements/delete.html",
        {
            "statement": statement,
            "tree_id": tree_id
        }
    )

def decision_tree_list(request):

    trees = DecisionTree.objects.all()

    return render(
        request,
        "statements/decision_tree_list.html",
        {
            "trees": trees
        }
    )

def decision_tree_create(request):

    if request.method == "POST":

        form = DecisionTreeForm(
            request.POST
        )

        if form.is_valid():

            form.save()

            return redirect(
                "statements:decision_tree_list"
            )

    else:

        form = DecisionTreeForm()

    return render(
        request,
        "statements/decision_tree_form.html",
        {
            "form": form,
            "title": "Create Decision Tree"
        }
    )

def decision_tree_update(
    request,
    pk
):

    tree = get_object_or_404(
        DecisionTree,
        pk=pk
    )

    if request.method == "POST":

        form = DecisionTreeForm(
            request.POST,
            instance=tree
        )

        if form.is_valid():

            form.save()

            return redirect(
                "statements:decision_tree_list"
            )

    else:

        form = DecisionTreeForm(
            instance=tree
        )

    return render(
        request,
        "statements/decision_tree_form.html",
        {
            "form": form,
            "title": "Update Decision Tree"
        }
    )

def decision_tree_delete(
    request,
    pk
):

    tree = get_object_or_404(
        DecisionTree,
        pk=pk
    )

    if request.method == "POST":

        tree.delete()

        return redirect(
            "statements:decision_tree_list"
        )

    return render(
        request,
        "statements/decision_tree_delete.html",
        {
            "tree": tree
        }
    )
