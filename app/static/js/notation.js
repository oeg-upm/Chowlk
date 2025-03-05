var specOntologists = document.getElementById("specification-ontologists");
var specDomainExperts = document.getElementById("specification-domain-experts");
var tocOntologists = document.getElementById("toc-ontologists");
var tocDomainExperts = document.getElementById("toc-domain-experts");
var btnOntologists = document.getElementById("btn-ontologists");
var btnDomainExperts = document.getElementById("btn-domain-experts");
var collapseButtons = document.getElementsByClassName("collapse-button");

console.log(collapseButtons);

for(let collapseButton of collapseButtons) {
    console.log(collapseButton);
    let rightArrow = collapseButton.getElementsByClassName("right-arrow")[0];
    console.log(rightArrow);
    let downArrow = collapseButton.getElementsByClassName("down-arrow")[0];
    console.log(downArrow);
    collapseButton.addEventListener("click", () => {
        console.log(collapseButton.getAttribute("data-target"));
        if(collapseButton.collapse){
            //collapseButton.src = "static/images/right-arrow.png";
            collapseButton.collapse = false;
            //document.getElementById(collapseButton.getAttribute("data-target")).style.display = 'none';
            rightArrow.style.display = '';
            downArrow.style.display = 'none';
        }
        else{
            //collapseButton.src = "static/images/down-arrow.png";
            collapseButton.collapse = true;
            //document.getElementById(collapseButton.getAttribute("data-target")).style.display = '';
            rightArrow.style.display = 'none';
            downArrow.style.display = '';
        }
        growDiv(collapseButton.getAttribute("data-target"));

    });
}

function growDiv(dataTarget) {
    var growDiv = document.getElementById(dataTarget + '-grow');
    if (growDiv.clientHeight) {
      growDiv.style.height = 0;
      growDiv.style.marginBottom = "";
    } else {
      var wrapper = document.getElementById(dataTarget);
      growDiv.style.height = wrapper.clientHeight + "px";
      growDiv.style.marginBottom = "1rem";
    }
  }

btnOntologists.addEventListener("click", ()=>{
    btnOntologists.classList.add("selected");
    btnDomainExperts.classList.remove("selected");

    tocOntologists.style.display = "block";
    tocDomainExperts.style.display = "none";

    specOntologists.style.display = "block";
    specDomainExperts.style.display = "none";
})

btnDomainExperts.addEventListener("click", ()=>{
    btnOntologists.classList.remove("selected");
    btnDomainExperts.classList.add("selected");

    tocOntologists.style.display = "none";
    tocDomainExperts.style.display = "block";

    specOntologists.style.display = "none";
    specDomainExperts.style.display = "block";

})