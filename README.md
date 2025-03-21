# ChefAI
![ChefAI Logo](front-end/public/images/chefai_logo.png)

ChefAI is a smart, user-friendly recipe generation web application that uses a Large Language Model (LLM) to suggest personalized recipes based on ingredients, dietary restrictions, cooking skill, and time availability. Users can interact with the platform either as guests or through a registered profile for enhanced features.

---

## Functionality

### For Unregistered Users:
- **Ingredient Input**: Users can list ingredients they have on hand.
- **Dietary Restrictions Input**: Users can specify their dietary needs seperated by a comma (e.g., vegan, gluten-free).
- **Skill Level Selector**: Users can indicate their cooking skill (e.g., beginner, intermediate, advanced).
- **Time Availability Selector**: Users can specify how much time they have to cook.
- **Generate Recipes Button**: Triggers recipe generation based on provided inputs.
- **Create Account Button**: Prompts user to register and gain access to additional features.

### For Registered Users:
- **All features available to unregistered users**, plus:
- **User Profile Creation**: Save dietary restrictions, skill level, name, and email.
- **Recipe History**: View previously generated recipes.
- **Saved Recipes Page**: Access a collection of saved recipes from past sessions.
- **Save Recipe Button**: Save generated recipes for later use.
- **Logout Option**: Log out and continue using the system as an unregistered user.

---

## Non-Functional Requirements

- **LLM Integration**: Core functionality (recipe generation) is powered by a Gemini API.
- **Performance**: Recipe generation should complete in at most 10 seconds.
- **Database Connectivity**: Persistent storage using an **SQL-based** Djnago model database.
- **Cross-Platform Compatibility**: Accessible on desktop, tablet, and mobile devices.
- **Intuitive UI**: The interface is simple and easy to use.
- **Secure Authentication**:
  - Registration requires **email** and **password**.
  - Passwords are stored using secure hashing practices.
- **Responsive Design**: Adaptable layout for different screen sizes to ensure seamless usability across devices.

---

## Installation

1. **Clone the repository:**
    ```
    git clone https://github.com/yourusername/chefai.git
    cd chefai
   ```
   
2. **Install Requirements:**
    Within a virtual environment run:
    ```
    pip install -r requirements.txt
    ```

3. **Open two terminals**
    ```bash
    cd back-end/cai_backend
    $ python manage.py runserver
    ```
    Open the second terminal
    ```bash
    cd front-end
    npm start
    ```

 