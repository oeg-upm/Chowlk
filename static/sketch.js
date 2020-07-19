function changeFileName() {

    var theFile = document.getElementById("files");
    var theText = document.getElementById("upload-text");
    fileName = this.value
    theText.innerHTML(fileName)

}