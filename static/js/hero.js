document.addEventListener("DOMContentLoaded", function () {

const sliders = document.querySelectorAll(".hero-slider");

sliders.forEach(slider => {

const slides = slider.querySelectorAll(".slide");
let index = 0;

if(slides.length > 0){

setInterval(()=>{

slides[index].classList.remove("active");

index = (index + 1) % slides.length;

slides[index].classList.add("active");

},4000);

}

});

});