(function ($) {
    $(document).on('content-editor:ready', function () {
        ContentEditor.addPluginButton(
            'app_richtext',
            '<i class="fas fa-pencil-alt"></i>'
        );
        ContentEditor.addPluginButton(
            'app_download',
            '<i class="fas fa-download"></i>'
        );
    });
})(django.jQuery);
