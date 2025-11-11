// ========== begin:: change picture input value handler ==========
$("[ImageInput]").change(function () {
    var x = $(this).attr("ImageInput");
    if (this.files && this.files[0]) {
        var reader = new FileReader();
        reader.onload = function (e) {
            $("[ImagePreview=" + x + "]").attr("src", e.target.result);
        };
        reader.readAsDataURL(this.files[0]);
    }
});
// ========== end:: change picture input value handler ==========
