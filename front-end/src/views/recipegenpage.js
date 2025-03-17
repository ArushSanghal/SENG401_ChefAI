import React, { Fragment, useState, useEffect } from 'react'

import './recipegenpage.css'
import '../components/food-form.css'

function Recipegenpage(){

    function handleSubmit(e){
        //prevent loading page
        e.preventDefault();

        // Read the form data
        const form = e.target;
        const formData = new FormData(form);

        // Convert string into a list
        const ingredientsList = formData.get("ingredients").split(",").map(item => item.trim());
        const dietaryList = formData.get("dietary_restrictions").split(",").map(item => item.trim());

        setLoading(true);
        // POST request using fetch()
        fetch("http://127.0.0.1:8000/generate_recipe/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },    
            body: JSON.stringify({
                ingredients: ingredientsList,
                skill_level: formData.get("skill_level"),
                dietary_restrictions: dietaryList,
                time: formData.get("time"),
        }),  
        })
        // Converting to JSON
        .then(response => response.json())
        // Displaying results to console
        .then(json => {
            setRecipe(json);
            setLoading(false);
        });

    }

    const [recipe, setRecipe] = useState(null);
    const [loading, setLoading] = useState(null);

    return (
    <>
    <title>ChefAI</title>
    <meta property="og:title" content="ChefAI" />

    <img src="/images/spaghetti-with-vegetables-cooking-in-a-pan.png" alt="frying pan" className="image"></img>
    <div className="thq-section-padding ">
    <div className = "formfield">
    <img
          alt= "A variety of vegetables and ingredients"
          src="/images/ingredients_image.jpg"
          className="thq-img-ratio-4-3 thq-flex-row thq-section-max-width food-form-max-width"
    />

        <form onSubmit={handleSubmit}>
    <div className = "form-content thq-section-padding"> 
        <h1>Make Your Recipe</h1>
        <div className = "ai-prompt-copy">
                Whether it's leftover ingredients, canned beans you don't know what to do with,
                or a dinner that needs some more inspiration,
                let ChefAI help you come up with a delicious recipe!
        </div>
        <div className = "firstdiv">
            <label>Ingredients: <hr />
                <input type = "text" name = "ingredients" required placeholder="tomatoes, onions, etc." className="writebox"/>
            </label>
        </div>
            <hr />
        <div className = "firstdiv">
            <label>Diet Restrictions: <hr/>
                <input type = "text" name = "dietary_restrictions" placeholder="vegan, vegetarian, etc." className="writebox"/>
            </label>
        </div>
            <hr />

        <div className = "skill-level-div">Skill Level: 
            <label >
                <input type = "radio" name = "skill_level" value = "beginner" required />Beginner
            </label>
            <label>
                <input type = "radio" name = "skill_level" value = "Intermediate" required />Intermediate
            </label>
            <label>
                <input type = "radio" name = "skill_level" value = "Advanced" required />Advanced
            </label>
        </div>
            <hr />
        <p className="time-p">Time Available: <hr/>
            <label>
                <input type = "radio" name= "time" value = "30"/>30 minutes
            </label>
            <label> 
                <input type = "radio" name= "time" value = "60"/>60 minutes
            </label>
            <label> 
                <input type = "radio" name= "time" value = "90"/>90 minutes
            </label>
            <label>
                <input type = "radio" name= "time" value = "120"/>120 minutes
            </label>
        </p>
        <div className = "recipe-button">
        <button type="submit" >Generate Recipe!</button>
        </div>
        </div> 
        
        </form>
        </div>
        <div className="generated-recipe">
            <h1 >Recipes! </h1>
            {loading && <h1>Loading.....</h1>}
            {recipe && (
                <div>
                <h4>Title: {recipe.recipe.recipe_name}</h4>
                <h5>Skill Level: {recipe.recipe.skill_level}</h5>
                <h5>Total Time: {recipe.recipe.time}</h5>
                <h5>Prep Time: {recipe.recipe.prep_time}</h5>
                <h5>Servings: {recipe.recipe.servings}</h5>
                <h5>Ingredients:</h5>
                <div >
                <ul>
                    {recipe.recipe.ingredients.map((ingredient) => (
                        <li>{ingredient.amount} {ingredient.unit} {ingredient.name}</li>
                    ))}
                </ul>
                </div>
                <h5>Steps:</h5>
                <ol>
                    {recipe.recipe.steps.map((step) => (
                        <li>{step.instruction}</li>
                    ))}
                </ol>
                </div>
            )}
        </div>

    </div>
    </>
    );
}

export default Recipegenpage;