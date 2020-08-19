// Going back to main view functionality
window.onpopstate = function (event){
    console.log(event.state.view);
    if (event.state.view === "main"){
        load_cards();
    };
};

document.addEventListener('DOMContentLoaded', function() {
    history.pushState({"view": "main"}, "", "");
    crosses = document.querySelectorAll(".cross");
    console.log(crosses);
    crosses.forEach(cross => {
        cross.onclick = cancel_card;
    });
    // Add maximize card view
    cards = document.querySelectorAll(".card-img-top");
    cards.forEach(card => {
        card.onclick = load_card;
    });
    // If the user is logged in
    if (document.querySelector("#pantry")){
        document.querySelector("#pantry").onclick = () => {
            hide(["recipes-view", "add-view", "recipe-view", "generate-view"]);
            show(["ingredients-view"]);    
    }
    document.querySelector("#add-items").onclick = () => {
        hide(["recipes-view", "ingredients-view", "recipe-view", "generate-view"]);
        show(["add-view"])};
    document.querySelector("#generate-recipes").onclick = () => {
        hide(["recipes-view", "ingredients-view", "recipe-view", "add-view"]);
        show(["generate-view"])};       
    };
    if (document.querySelector("#add")){
        document.querySelector("#add").onclick = add;
        document.querySelector("#input-ingredient").addEventListener ('keypress', function(event) {
            if (event.key === 'Enter'){
                add();
            }
        });
        document.querySelector("#save-all").onclick = submit_ingredients;
        document.querySelectorAll(".edit").forEach (edit_button => 
            edit_button.onclick = toggle_edit);
    }
    document.querySelector("#alert").onclick = () => {hide(["alert"])}
});

function cancel_card(){
const parent = this.parentElement;
parent.parentElement.style.animationPlayState = "running";
parent.parentElement.addEventListener('animationend', () => {
    parent.parentElement.style.animationPlayState = "paused";
    var loader = document.createElement('div');
    loader.className = "loader";
    parent.append(loader);
    this.remove()});

    // Fetch and get the new recipe
    var img = parent.parentElement.querySelector(".card-img-top");
    fetch(`/generate/1?swap=${img.dataset.id}`, {
        method: 'POST',
        headers:{'X-CSRFToken': get_token()},
      })
      .then(response => response.json()) 
      .then(result => {       
        // Stop the animation and revert opacity
        parent.parentElement.querySelector('.loader').remove();
        parent.parentElement.style.animationFillMode = "backwards";
        // Load the new recipe
        parent.parentElement.querySelector('.card-title').innerHTML = result.title;
        img.src = result.img;
        img.dataset.id = result.id;
        parent.parentElement.querySelector('.card-text').innerHTML = `<strong>Potentially missing:</strong> ${result.missing}`;
      });
}
// Three functions below pulled from code I wrote for Project 4
function hide(inputs) {
    // Hides any view by id
    inputs.forEach(input =>{
        document.querySelector(`#${input}`).style.display = 'none';
    })
}
function show(inputs) {
    // Shows any view by id
    inputs.forEach(input =>{
        document.querySelector(`#${input}`).style.display = 'block';
    })
}
function get_token(){
    // Gets necessary token for django requests
    return Cookies.get('csrftoken');
}
function submit_ingredients(){
    fetch('/pantry/submit', {
        method: 'POST',
        headers:{'X-CSRFToken': get_token()},
        body: JSON.stringify({
            body: document.querySelector('#added-items').innerText
        })
    })
    .then(response => response.json())
    .then(() => location.reload());
  }
function add(){
    var item = document.querySelector('#input-ingredient');
    // Only add ingredient if the user typed something
    if (item.value){
        var point = document.createElement('p');
        point.className = "thin";
        point.innerHTML = item.value;
        document.querySelector("#added-items").append(point);
        item.value = '';
    }
}
function toggle_edit(){
    // Change the button and what it does
    this.innerHTML = "Save";
    this.className = "btn btn btn-outline-success btn-sm edit";

    // Prefill an input with the old number
    var row = this.parentElement.parentElement;
    var quantity = row.querySelector(".quantity");

    // Change what clicking the button does
    this.onclick = () => {
        push_edit(quantity.dataset.id, input_form.value);
        quantity.innerHTML = input_form.value;
        input_form.remove();
    };
    var input_form = document.createElement('input');
    input_form.className = "form-control narrow";
    input_form.type = "number";
    input_form.min = 0;
    input_form.value = quantity.innerHTML;
    quantity.innerHTML = '';
    quantity.append(input_form);
}
function push_edit(id, value){
    // Perform the actual edit
    fetch(`/pantry/edit/${id}`, {
        method: 'PUT',
        headers: {'X-CSRFToken': get_token()},
        body: JSON.stringify({
            value: value
        })})
        .then(response => response.json())
        .then(result => console.log(result));
    // Change the button back to edit mode
    event.target.className = "btn btn btn-outline-primary btn-sm edit";
    event.target.innerHTML = 'Edit';
    event.target.onclick = toggle_edit;
}
function refresh_pantry(){
    //TO DO
}
function load_card(){
    // Load a large card with all data for one recipe
    var recipe = document.querySelector("#recipe-view");
    var card = recipe.querySelector(".card");

    // Swap In New Information
    var id = parseInt(this.dataset.id);
    fetch(`recipe/${id}`)
    .then(response => response.json())
    .then(result => {
        card.querySelector(".card-img-top").src = result.img;
        card.querySelector(".card-title").innerHTML = result.title;
        card.querySelector(".source").setAttribute('href', result.url);
        var steps_div = card.querySelector(".steps");
        var list = card.querySelector(".list-group");
        list.innerHTML = '';
        steps_div.innerHTML = '';
        var ingredients = result.ingredients;
        // Source: https://stackoverflow.com/questions/46334292/foreach-not-a-function-javascript
        Object.keys(ingredients).forEach(key => {
            var li = document.createElement('li');
            li.className = "list-group-item";
            li.innerHTML = key;
            list.append(li);
        });
        var steps = result.steps;
        var step_counter = 1;
        Object.keys(steps).forEach(key => {
            var step_count = document.createElement('h5');
            step_count.innerHTML = `Step ${step_counter}`;
            var step_text = document.createElement('p');
            step_text.innerHTML = key;
            steps_div.append(step_count, step_text);
            step_counter++;
        });
    });

    hide(["recipes-view"]);
    show(["recipe-view"]);
    history.pushState({"view": "main"}, "", "");
    // Source: https://stackoverflow.com/questions/1144805/scroll-to-the-top-of-the-page-using-javascript
    window.scrollTo(0, 60);
}

function load_cards(){
    hide(["recipe-view", "ingredients-view", "add-view", "generate-view"]);
    show(["recipes-view"]); 
}