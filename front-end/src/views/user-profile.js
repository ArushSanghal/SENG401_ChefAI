import React, { useEffect, useState } from "react";
import { useHistory } from "react-router-dom";

import Navbar8 from '../components/navbar8'

const UserProfile = () => {
    const [showButton, setShowButton] = useState(true);
    const [userData, setUserData] = useState(null);
    const [skillLevel, setSkillLevel] = useState("");
    const [dietaryRestrictions, setDietaryRestrictions] = useState("");
    const [recipe, setRecipe] = useState(null);
    const [loading, setLoading] = useState(null);
    const [increment, setIncrement] = useState(0);
    const [save, setSave] = useState(false);
    const [savedRecipes, setSavedRecipes] = useState(false);
    const [viewRecipes, setViewRecipes] = useState(false);
    const history = useHistory();

    useEffect(() => {
        const fetchUserData = async () => {
            const token = localStorage.getItem("access_token");
            if (!token) {
                history.push("/");
                return;
            }

            try {
                const response = await fetch("http://127.0.0.1:8000/user/", {
                    method: "GET",
                    headers: {
                        "Authorization": `Bearer ${token}`,
                    },
                });
                const data = await response.json();
                if (response.ok) {
                    setUserData(data);
                    setSkillLevel(data.skill_level);
                    setDietaryRestrictions(data.dietary_restrictions.join(", "));
                } else {
                    localStorage.removeItem("access_token");
                    localStorage.removeItem("refresh_token");
                    history.push("/");
                }
            } catch (error) {
                console.error("Error:", error);
            }
        };

        fetchUserData();
    }, [history, increment]);

    const handleSave = () => {
        const token = localStorage.getItem("access_token");
        if (!token) {
            history.push("/"); //Back to main page when token is expired
            return;
        }
    
        fetch("http://127.0.0.1:8000/update-user/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`,
            },
            body: JSON.stringify({
                skill_level: skillLevel,
                dietary_restrictions: dietaryRestrictions.split(",").map(r => r.trim()),
            }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert("Profile updated!");
                
                setUserData(prev => ({
                    ...prev,
                    skill_level: skillLevel,
                    dietary_restrictions: dietaryRestrictions.split(",").map(r => r.trim()),
                }));
            } else {
                alert("Error updating profile.");
            }
        })
        .catch(error => console.log(error));
    };


    if (!userData) {
        return <div>Loading...</div>;
    }

    function handleSubmit(e){
        //prevent loading page
        e.preventDefault();

        // Read the form data
        const form = e.target;
        const formData = new FormData(form);

        // Convert string into a list
        const ingredientsList = formData.get("ingredients").split(",").map(item => item.trim());
        //const dietaryList = formData.get("dietary_restrictions").split(",").map(item => item.trim());

        const token = localStorage.getItem("access_token");

        setLoading(true);
        // POST request using fetch()
        fetch("http://127.0.0.1:8000/generate_recipe/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`,
            },    
            body: JSON.stringify({
                ingredients: ingredientsList,
                skill_level: skillLevel,
                dietary_restrictions: dietaryRestrictions.split(",").map(r => r.trim()),
                time: formData.get("time"),
        }),  
        })
        // Converting to JSON
        .then(response => response.json())
        // Displaying results to console
        .then(json => {
            setRecipe(json);
            setLoading(false);
            setSave(true);
        });

    }

    function handleSaveButton(e){
        //increment to fetch the data
        setIncrement(increment + 1);

        e.preventDefault();

        const token = localStorage.getItem("access_token");
            if (!token) {
                history.push("/");
                return;
            }

        const useremail = userData.email
        const username = userData.username

        console.log(useremail)
        console.log(token)

        fetch("http://127.0.0.1:8000/save_button/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`,
            },    
            body: JSON.stringify({
                useremail: useremail,
                username: username,
        }),  
        })
        // Converting to JSON
        .then(response => response.json())
        // Displaying results to console
        .then(json => {
            console.log("Username and Email has been sent to the backend");
            console.log(json);
        })
        .then(setShowButton(false), alert("Recipe Saved Succesfully"));
    }
    
    return (
        <div>
            <Navbar8></Navbar8>
            <img src="/images/spaghetti-with-vegetables-cooking-in-a-pan.png" alt="frying pan" className="image"></img>
            <div className="thq-flex-row thq-flex-column">
                <h1>Welcome, {userData.first_name}!</h1>
                <p><strong>Email:</strong> {userData.email}</p>
                <p><strong>Username:</strong> {userData.username}</p>

                <label>Skill Level:</label>
                <select value={skillLevel} onChange={(e) => setSkillLevel(e.target.value)}>
                    <option value="Beginner">Beginner</option>
                    <option value="Intermediate">Intermediate</option>
                    <option value="Advanced">Advanced</option>
                </select>
                <div>
                </div>
                <label>Dietary Restrictions:</label>
                <div className="thq-section-padding-smaller">
                </div>
                <input 
                    className="thq-input"
                    type="text"
                    value={dietaryRestrictions}
                    onChange={(e) => setDietaryRestrictions(e.target.value)}
                    placeholder="Separated by commas"
                />
                <div className="thq-section-padding-smaller">
                </div>

                <button className="thq-button-animate thq-button-filled" onClick={handleSave} style={{ border: "1px solid #ddd" }}>Save Changes</button>
            </div>

            {loading && <p>Loading...</p>}
            <div>
                {Array.isArray(savedRecipes) && viewRecipes && (
                    savedRecipes.map((recipe, index) => (
                        <div key={index} style={{ marginBottom: "20px", border: "1px solid #ddd", padding: "10px" }}>
                            <p><strong>Recipe Name:</strong>{recipe.recipe_name}</p>
                            <p><strong>Estimated Time:</strong> {recipe.estimated_time}</p>
                            <p><strong>Skill Level:</strong> {recipe.skill_level}</p>
                            <p><strong>Ingredients:</strong> {recipe.ingredients}</p>

                            <h4>Instructions:</h4>
                                <ol style={{ paddingLeft: "20px" }}>
                                    {JSON.parse(recipe.instructions).map((instruction, stepIndex) => (
                                        <li key={stepIndex}>
                                            {instruction.instruction || "No instruction available."}
                                        </li>
                                    ))}
                                </ol>
                        </div>
                    ))
                ) }
        </div>
            <title>ChefAI</title>
    <meta property="og:title" content="ChefAI" />

    <div className="thq-section-padding ">
    <div className = "formfield">
    <img
          alt= "A variety of vegetables and ingredients"
          src="/images/ingredients_image.jpg"
          className="thq-img-ratio-4-3 thq-flex-row thq-section-max-width food-form-max-width"
    />
    <div className = 'form-text thq-section-padding'>
    <form onSubmit={handleSubmit}>
    <div className = "form-content"> 
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
        <label>Dietary Restrictions:</label>
            <input type="text" value={dietaryRestrictions} disabled className="writebox" />

        <label>Skill Level:</label>
            <input type="text" value={skillLevel} disabled className="writebox" />
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
        <button className="thq-button-animated thq-button-filled-big thq-heading-3" type="submit" >Generate Recipe!</button>
        </div> 
        
        </form>
        </div>
        </div>
        <div className="generated-recipe">
            <h1 className="thq-heading-1">Recipe! </h1>
            {loading && <h1>Loading.....</h1>}
            {recipe && (
                <div>
                <h4 className="thq-heading-2">Title: {recipe.recipe.recipe_name}</h4>
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
            {save && showButton && <button className="thq-button-animated thq-button-filled" onClick={ handleSaveButton }>Save Recipe</button>}
        </div>

    </div>
        </div>
        
    );
};

export default UserProfile;