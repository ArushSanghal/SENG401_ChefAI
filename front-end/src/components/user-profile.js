import React, { useEffect, useState } from "react";
import { useHistory } from "react-router-dom";

const UserProfile = () => {
    const [userData, setUserData] = useState(null);
    const [skillLevel, setSkillLevel] = useState("");
    const [dietaryRestrictions, setDietaryRestrictions] = useState("");
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
    }, [history]);

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

    const handleSignOut = async () => {
        const token = localStorage.getItem("access_token");
        if (!token) {
            history.push("/");
            return;
        }
    
        try {
            const response = await fetch("http://127.0.0.1:8000/logout/", {
                method: "POST",
                headers: {
                    "Authorization": `Bearer ${token}`,
                },
            });
            if (response.ok) {
                localStorage.removeItem("access_token");
                localStorage.removeItem("refresh_token");
                history.push("/");
            } else {
                alert("Error logging out.");
            }
        } catch (error) {
            console.error("Error:", error);
        }
    };

    if (!userData) {
        return <div>Loading...</div>;
    }

    return (
        <div>
            <h1>Welcome, {userData.first_name}!</h1>
            <p><strong>Email:</strong> {userData.email}</p>
            <p><strong>Username:</strong> {userData.username}</p>

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
            <button onClick={handleSignOut}>Sign Out</button>
        </div>
    );
};

export default UserProfile;