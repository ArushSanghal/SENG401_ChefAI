import React, { Fragment, useState } from 'react'

import PropTypes from 'prop-types'

import './food-form.css'

const FoodForm = (props) => {

    const [title, setTitle] = useState("");
    const [body, setBody] = useState("");
    const [authUsername, setAuthUsername] = useState("");
    const [adminFlag, setAdminFlag] = useState("");
  
    function addNewBlogPost() {
      fetch(("http://localhost:3000/blog/posts"), {
        method: "POST",
        body: JSON.stringify({
          title: title,
          body: body,
          authorID: authUsername,
          adminFlag : false,
        }),
        headers: {
            "Content-Type": "application/json"
        }
      })
        /*.then((response) => response.json())
        .then((data) => {
          setContent(data);
          console.log(data);
        })
        .catch((error) => console.log(error));*/
    }


  return (
    <div className="food-form-contact9 thq-section-padding">
      <div className="thq-flex-row thq-section-max-width food-form-max-width">
        <img
          alt={props.imageAlt}
          src={props.imageSrc}
          className="food-form-image1 thq-img-ratio-4-3"
        />
        <div className="food-form-content1 thq-flex-column">
          <div className="food-form-section-title thq-card">
            <div className="food-form-content2">
              <h2 className="thq-heading-2">
                {props.heading1 ?? (
                  <Fragment>
                    <span className="food-form-text7">
                      Tell us - what's in your fridge?
                    </span>
                  </Fragment>
                )}
              </h2>
            </div>
              <div>
                Whether it's leftover ingredients, canned beans you don't know what to do with,
                let us help you make use of every cent of your food.
              </div>
          </div>
          <form className="thq-card"  onSubmit={(e) => {
            e.preventDefault();
            addNewBlogPost();
          }}>
            <div className="food-form-input1">
              <label htmlFor="contact-form-3-name" className="thq-body-small">
                Title
              </label>
              <input
                type="text"
                id="contact-form-3-name"
                placeholder="Title"
                rows="Title"
                className="thq-input"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
              />
            </div>
            <div className="food-form-input2">
              <label htmlFor="contact-form-3-email" className="thq-body-small">
                Username
              </label>
              <input
                type="text"
                id="contact-form-3-email"
                required={true}
                placeholder="Username"
                className="thq-input"
                value={authUsername}
                onChange={(e) => setAuthUsername(e.target.value)}
              />
            </div>
            <div className="food-form-container">
              <label
                htmlFor="contact-form-3-message"
                className="thq-body-small"
              > Blog Post
              </label>
              <textarea
                id="contact-form-3-message"
                rows="3"
                placeholder="Enter your text here"
                className="thq-input"
                value={body}
                onChange={(e) => setBody(e.target.value)}
              ></textarea>
            </div>
            <button
              type="submit"
              className="food-form-button thq-button-filled"
            >
              <span className="thq-body-small">
                {props.action ?? (
                  <Fragment>
                    <span className="food-form-text6">Submit</span>
                  </Fragment>
                )}
              </span>
            </button>
          </form>
        </div>
      </div>
    </div>
  )
}

FoodForm.defaultProps = {
  imageSrc:'/images/ingredients_image.jpg',
  action: undefined,
  imageAlt: 'A picture of vegtables and various ingredients',
  heading1: undefined,
}

FoodForm.propTypes = {
  imageSrc: PropTypes.string,
  action: PropTypes.element,
  imageAlt: PropTypes.string,
  heading1: PropTypes.element,
}

export default FoodForm
