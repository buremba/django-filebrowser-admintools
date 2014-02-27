var FileBrowserDialogue = {
    init: function () {
        // remove tinymce stylesheet.
        var allLinks = document.getElementsByTagName("link");
        allLinks[allLinks.length - 1].parentNode.removeChild(allLinks[allLinks.length - 1]);
    },
    fileSubmit: function (FileURL) {
        var getParameterByName = function (name) {
            name = name.replace(/[\[]/, "\\\[").replace(/[\]]/, "\\\]");
            var regex = new RegExp("[\\?&]" + name + "=([^&#]*)"),
                results = regex.exec(location.search);
            return results == null ? "" : decodeURIComponent(results[1].replace(/\+/g, " "));
        }
        window.parent.document.getElementById(getParameterByName("tag_name")).value = FileURL;
        window.parent.tinymce.activeEditor.windowManager.close();
    }
}
