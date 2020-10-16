var pFilename = document.getElementById("filename");
var inputFile = document.getElementById("file");
var resetButtton = document.getElementById("reset");
var submitButton = document.getElementById("submit");
var errorMessage = document.getElementById("error-message");

inputFile.addEventListener("change", ()=>{
    var filepath = inputFile.value
    var filename_array = filepath.split("\\")
    pFilename.innerText = filename_array[filename_array.length - 1]
    errorMessage.style.visibility = "hidden"
})

resetButtton.addEventListener("click", ()=>{
    pFilename.innerText = ""
    errorMessage.style.visibility = "hidden"
})