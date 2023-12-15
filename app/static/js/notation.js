var specOntologists = document.getElementById("specification-ontologists")
var specDomainExperts = document.getElementById("specification-domain-experts")
var tocOntologists = document.getElementById("toc-ontologists")
var tocDomainExperts = document.getElementById("toc-domain-experts")
var btnOntologists = document.getElementById("btn-ontologists")
var btnDomainExperts = document.getElementById("btn-domain-experts")

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