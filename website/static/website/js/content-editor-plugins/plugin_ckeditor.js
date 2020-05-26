/* global django, CKEDITOR */
(function ($) {

    /* Improve spacing */
    var style = document.createElement('style');
    style.type = 'text/css';
    style.innerHTML = "div[id*='cke_id_'] {margin-left:170px;}";
    $('head').append(style);

    CKEDITOR.config.width = '787';
    CKEDITOR.config.height = '300';
    CKEDITOR.config.format_tags = 'p;h1;h2;h3;h4;pre';
    CKEDITOR.config.toolbar = [[
        'Maximize', '-',
        'Format', '-',
        'Bold', 'Italic', 'Underline', 'Strike', '-',
        'Subscript', 'Superscript', '-',
        'NumberedList', 'BulletedList', '-',
        'Anchor', 'Link', 'Unlink', '-',
        'Source'
    ]];

    // Activate and deactivate the CKEDITOR because it does not like
    // getting dragged or its underlying ID changed.
    // The 'data-processed' attribute is set for compatibility with
    // django-ckeditor. (Respectively to prevent django-ckeditor's
    // ckeditor-init.js from initializing CKEditor again.)

    $(document).on(
        'content-editor:activate',
        function (_event, $row, _formsetName) {
            $row.find('textarea[data-type=ckeditortype]').each(function () {
                if (this.getAttribute('data-processed') != '1') {
                    this.setAttribute('data-processed', '1')
                    $($(this).data('external-plugin-resources')).each(function () {
                        CKEDITOR.plugins.addExternal(this[0], this[1], this[2]);
                    });
                    CKEDITOR.replace(this.id, $(this).data('config'));
                }
            });
        }
    ).on(
        'content-editor:deactivate',
        function _(event, $row, _formsetName) {
            $row.find('textarea[data-type=ckeditortype]').each(function () {
                try {
                    CKEDITOR.instances[this.id] && CKEDITOR.instances[this.id].destroy();
                    this.setAttribute('data-processed', '0')
                } catch (err) { }
            });
        }
    );
})(django.jQuery);
