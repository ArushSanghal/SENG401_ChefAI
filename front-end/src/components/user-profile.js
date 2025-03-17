import React, { useContext, useState } from "react";
import { CurrentUserContext } from "../index";

const UserProfile = () => {
    const { currentUser, setCurrentUser } = useContext(CurrentUserContext);
    const [skillLevel, setSkillLevel] = useState(currentUser.skill_level);
    const [dietaryRestrictions, setDietaryRestrictions] = useState(currentUser.dietary_restrictions.join(", "));

    const handleSave = () => {
        fetch("http://127.0.0.1:8000/update-user/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Token ${localStorage.getItem("authToken")}`
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
                setCurrentUser(prev => ({
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

    return (
        <div>
            <h1>Welcome, {currentUser.first_name}!</h1>
            <p><strong>Email:</strong> {currentUser.email}</p>
            <p><strong>Username:</strong> {currentUser.username}</p>

            <label>Skill Level:</label>
            <select value={skillLevel} onChange={(e) => setSkillLevel(e.target.value)}>
                <option value="Beginner">Beginner</option>
                <option value="Intermediate">Intermediate</option>
                <option value="Advanced">Advanced</option>
            </select>

            <label>Dietary Restrictions:</label>
            <input 
                type="text"
                value={dietaryRestrictions}
                onChange={(e) => setDietaryRestrictions(e.target.value)}
                placeholder="Enter dietary restrictions, separated by commas"
            />

            <button onClick={handleSave}>Save Changes</button>
        </div>
    );
};

export default UserProfile;
