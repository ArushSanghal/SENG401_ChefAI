import React, { Fragment, useState, useEffect } from 'react'

import { Helmet } from 'react-helmet'

import Navbar8 from '../components/navbar8'
import BlogPostHeader2 from '../components/blog-post-header2'
import Footer41 from '../components/footer41'
import './savedrecipes.css'
import Banner11 from '../components/banner11'
import { Link } from 'react-router-dom/cjs/react-router-dom'

const SavedRecipes = (props) => {

  const [content, setContent] = useState(null);
  useEffect(() => {
    fetch("http://127.0.0.1:8000/view_recipes/", {
      method: "GET",
    })
      .then((response) => response.json())
      .then((data) => {
        setContent(data);
        console.log(data);
      })
      .catch((error) => console.log(error));
  }, []);



  return (
    <div className="blog-container">
      <Helmet>
        <title>ChefAI</title>
        <meta property="og:title" content="ChefAI" />
      </Helmet>

      <Navbar8
      ></Navbar8>

      <Banner11
        heading1={
          <Fragment>
            <span className="banner11-text5">Saved Recipes</span>
          </Fragment>
        }            
        content1={
          <Fragment>
            <span className="banner11-text3">
              View your previously saved recipes and re-create classic masterpieces!</span>
          </Fragment>
        }
      ></Banner11>

      {content?.map((content) => (
              <BlogPostHeader2
              date={
                <Fragment>
                  <span className="blog-text24">{content.instructions}</span>
                </Fragment>
              }
              blogPostTitle={
                <Fragment>
                  <span className="blog-text25">{content.title}</span>
                </Fragment>
              }
              readTime={
                <Fragment/>
              }
              category={
                <Fragment>
                  <span className="blog-text27">Estimated Time: {content.estimated_time}</span>
                </Fragment>
              }
              avatarName={
                <Fragment>
                  <span className="blog-text28">Skill level: {content.skill_level}</span>
                </Fragment>
              }
            ></BlogPostHeader2>
      ))}


    </div>
  )
}


export default SavedRecipes
