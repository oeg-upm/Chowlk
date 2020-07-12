var dropzone;

function setup(){

    dropzone = select("#dropzone");
    dropzone.dragOver(highlight);
    dropzone.dragLeave(unhighlight);
    dropzone.drop(gotFile, unhighlight);
 
}

function highlight() {
    dropzone.style("background-color", "#ccc");
}

function unhighlight() {
    dropzone.style("background-color", "#fff");
}

function gotFile(file){
    var html_form = document.forms.namedItem("formzone");
    var html_div = document.getElementById("result");
    dropzone.html(file.name);

    html_form.addEventListener("submit", function(ev){
        
        var js_form = new FormData(html_form);

        js_form.append("diagram_data", file.file);
        var request = new XMLHttpRequest();
        request.open("POST", "/diagram_upload");
        request.onload = function(oEvent){

            if (request.status == 200){
                html_div.innerHTML = "Uploaded!";
            } else {
                html_div.innerHTML = "Error " + request.status + " occurred when trying to upload your file.<br \/>";
            }
        };        
        
        request.send(js_form);
        ev.preventDefault();
    }, false);

}