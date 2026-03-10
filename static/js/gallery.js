document.addEventListener("DOMContentLoaded",function(){


/* FILTER */

const filterBtns=document.querySelectorAll(".gallery-filter button");
const cards=document.querySelectorAll(".gallery-card");

filterBtns.forEach(btn=>{

btn.addEventListener("click",()=>{

const filter=btn.dataset.filter;

cards.forEach(card=>{

if(filter==="all"||card.dataset.category===filter){
card.style.display="block";
}else{
card.style.display="none";
}

});

});

});


/* LIKE BUTTON */

function attachLikeButtons(){

document.querySelectorAll(".like-btn").forEach(btn=>{

btn.onclick=function(){

let count=this.querySelector("span");

let num=parseInt(count.textContent);

count.textContent=num+1;

};

});

}

attachLikeButtons();


/* LIGHTBOX */

const lightbox=document.getElementById("lightbox");
const lightboxImg=document.getElementById("lightboxImage");

document.querySelectorAll(".gallery-grid img").forEach(img=>{

img.onclick=function(){

lightbox.style.display="flex";
lightboxImg.src=this.src;

};

});

document.querySelector(".close-lightbox").onclick=()=>{

lightbox.style.display="none";

};


/* UPLOAD */

const form=document.getElementById("uploadForm");
const grid=document.getElementById("galleryGrid");

form.addEventListener("submit",function(e){

e.preventDefault();

const file=document.getElementById("imageUpload").files[0];
const reader=new FileReader();

const username=document.getElementById("username").value;
const caption=document.getElementById("caption").value;
const destination=document.getElementById("destination").value;

reader.onload=function(event){

const card=document.createElement("div");
card.className="gallery-card";
card.dataset.category=destination;

card.innerHTML=`
<img src="${event.target.result}">
<div class="card-info">
<span class="username">${username}</span>
<p>${caption}</p>
<div class="like-btn">❤️ <span>0</span></div>
</div>
`;

grid.prepend(card);

attachLikeButtons();

};

reader.readAsDataURL(file);

form.reset();

});

});