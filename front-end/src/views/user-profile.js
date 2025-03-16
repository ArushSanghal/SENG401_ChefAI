import React, { useContext, useEffect, useState } from "react";
import { CurrentUserContext } from "../index";

const UserProfile = () => {
    const { currentUser } = useContext(CurrentUserContext);
    const [profileData, setProfileData] = useState(null);

    useEffect(() => {
        const fetchProfile = async () => {
            try {
                const token = localStorage.getItem("access_token"); // Get JWT from localStorage
        
                const response = await fetch("http://127.0.0.1:8000/api/user-profile/", {
                    method: "GET",
                    headers: {
                        "Authorization": `Bearer ${token}`, // Attach token
                        "Content-Type": "application/json",
                    },
                });
        
                if (response.status === 401) {
                    throw new Error("Unauthorized - Please log in again.");
                }
        
                if (!response.ok) {
                    throw new Error("Failed to fetch profile");
                }
        
                const data = await response.json();
                console.log("User Profile:", data);
                setProfileData(data);
            } catch (error) {
                console.error("Error:", error);
            }
        };
        
        

        fetchProfile();
    }, []);

    if (!profileData) {
        return <p>Loading profile...</p>;
    }

    return (
        <div>
            <h1>Welcome, {profileData.first_name}!</h1>
            <p>Email: {profileData.email}</p>
            <p>Username: {profileData.username}</p>
            <p>Skill Level: {profileData.skill_level}</p>
            <p>Available Time: {profileData.available_time}</p>
        </div>
    );
};

export default UserProfile;
