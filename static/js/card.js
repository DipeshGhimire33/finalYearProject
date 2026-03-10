document.querySelectorAll(".clickable-card").forEach(card => {

card.addEventListener("click", function(){

const link = this.dataset.link;

if(link){
window.location.href = link;
}

});

});