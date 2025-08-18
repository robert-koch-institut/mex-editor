window.mexEditor = {
    changes: false
}

window.onbeforeunload = function () {
    if (window.mexEditor.changes) {
        return 'Are you sure you want to leave? Unsaved changes will be lost.';
    }
};
if (typeof window !== "undefined" && window.next) {
    window.next.router.beforePopState(({ url, as, options }) => {
        result = window.mexEditor.changes ? confirm("Are you sure you want to leave? Unsaved changes will be lost.") : true;
        if (result) {
            window.mexEditor.changes = false;
        }
        return result;
    });
}

window.updateMexEditorChanges = function (value) {
    window.mexEditor.changes = value;
}
