document.addEventListener("DOMContentLoaded", function(){

let comments = JSON.parse(localStorage.getItem("comments")) || [];

const form = document.getElementById("commentForm");
const list = document.getElementById("commentsList");
const stars = document.querySelectorAll("#starRating span");

let rating = 0;


/* STAR SELECTION */

stars.forEach(star=>{
star.addEventListener("click",()=>{

rating = star.dataset.value;

stars.forEach(s=>s.classList.remove("active"));

for(let i=0;i<rating;i++){
stars[i].classList.add("active");
}

});
});


/* SUBMIT COMMENT */

form.addEventListener("submit",function(e){

e.preventDefault();

const name = document.getElementById("commentName").value;
const text = document.getElementById("commentText").value;

const comment = {
id:Date.now(),
name:name,
text:text,
rating:rating,
likes:0,
replies:[]
};

comments.unshift(comment);

saveComments();

form.reset();
stars.forEach(s=>s.classList.remove("active"));
rating = 0;

renderComments();

});


/* SAVE TO LOCAL STORAGE */

function saveComments(){
localStorage.setItem("comments",JSON.stringify(comments));
}


/* RENDER COMMENTS */

function renderComments(){

list.innerHTML="";

comments.forEach(comment=>{

const card=document.createElement("div");
card.className="comment-card";

const avatar=comment.name.charAt(0).toUpperCase();

card.innerHTML=`

<div class="avatar">${avatar}</div>

<div class="comment-body">

<div class="comment-header">
<span class="comment-name">${comment.name}</span>
<span class="comment-rating">${"★".repeat(comment.rating)}</span>
</div>

<div class="comment-text">${comment.text}</div>

<div class="comment-actions">
<span class="like-btn">❤️ ${comment.likes}</span>
</div>

</div>
`;

list.appendChild(card);

const likeBtn = card.querySelector(".like-btn");

likeBtn.addEventListener("click",()=>{

comment.likes++;

saveComments();

renderComments();

});

});

updateRating();

}


/* CALCULATE AVERAGE RATING */

function updateRating(){

if(comments.length === 0) return;

let total = 0;

comments.forEach(c=>{
total += Number(c.rating);
});

const avg = (total/comments.length).toFixed(1);

document.getElementById("avgRating").innerText = avg;

document.getElementById("totalReviews").innerText =
comments.length + " Reviews";

}

renderComments();

});