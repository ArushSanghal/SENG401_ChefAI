import React, { Fragment, useState, useEffect } from 'react';
import { Helmet } from 'react-helmet';
import Navbar8 from '../components/navbar8';
import BlogPostHeader2 from '../components/blog-post-header2';
import Footer41 from '../components/footer41';
import './savedrecipes.css';
import Banner11 from '../components/banner11';
import { Link } from 'react-router-dom/cjs/react-router-dom';

const SavedRecipes = (props) => {
  const [content, setContent] = useState(null);

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (!token) {
      // Handle the case where the token is not available, e.g., redirect to login
      return;
    }

    fetch("http://127.0.0.1:8000/view_recipes/?type=saved", {
      method: "GET",
      headers: {
        "Authorization": `Bearer ${token}`,
      },
    })
      .then((response) => response.json())
      .then((data) => {
        setContent(data.saved_recipes); // Assuming the response structure is { saved_recipes: [...] }
        console.log(data);
      })
      .catch((error) => console.log(error));
  }, []);

  const renderInstructions = (instructions) => {
    try {
      // Parse the instructions field
      const parsedInstructions = JSON.parse(instructions);

      // Check if parsedInstructions is an array
      if (Array.isArray(parsedInstructions)) {
        return (
          <ol>
            {parsedInstructions.map((step, index) => (
              <li key={index}>
                {/* Ensure the step object has the correct key (e.g., "Instruction") */}
                {step.Instruction || step.instruction || "No instruction available."}
              </li>
            ))}
          </ol>
        );
      } else {
        // If it's not an array, display the raw instructions
        return <p>{instructions}</p>;
      }
    } catch (error) {
      console.error("Failed to parse instructions:", error);
      // If parsing fails, display the raw instructions
      return <p>{instructions}</p>;
    }
  };

  return (
    <div className="blog-container">
      <Helmet>
        <title>ChefAI</title>
        <meta property="og:title" content="ChefAI" />
      </Helmet>

      <Navbar8></Navbar8>

      <Banner11
        heading1={
          <Fragment>
            <span className="banner11-text5">Saved Recipes</span>
          </Fragment>
        }
        content1={
          <Fragment>
            <span className="banner11-text3">
              View your previously saved recipes and re-create classic masterpieces!
            </span>
          </Fragment>
        }
      ></Banner11>

      {content?.map((recipe, index) => (
        <BlogPostHeader2
          key={index}
          date={
            <Fragment>
              <span className="blog-text24">{renderInstructions(recipe.instructions)}</span>
            </Fragment>
          }
          blogPostTitle={
            <Fragment>
              <span className="blog-text25">{recipe.recipe_name}</span>
            </Fragment>
          }
          readTime={<Fragment />}
          category={
            <Fragment>
              <span className="blog-text27">Estimated Time: {recipe.estimated_time}</span>
            </Fragment>
          }
          avatarName={
            <Fragment>
              <span className="blog-text28">Skill level: {recipe.skill_level}</span>
            </Fragment>
          }
        ></BlogPostHeader2>
      ))}
    </div>
  );
};

export default SavedRecipes;