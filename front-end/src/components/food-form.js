import React, { Fragment, useState } from 'react'

import PropTypes from 'prop-types'

import './food-form.css'

const FoodForm = (props) => {

    const [diet_restrictions, set_diet_restrictions] = useState("");
    const [ingredients, set_ingredients] = useState("");
    const [available_time, set_available_time] = useState("");
    const [skill_level, set_skill_level] = useState("");
  
    function createNewRecipe() {
      fetch(("http://localhost:3000/"/* The rest of the path for the backend */), {
        method: "POST",
        body: JSON.stringify({
          ingredients: ingredients,
          diet_restrictions: diet_restrictions,
          available_time: available_time,
          skill_level : skill_level,
        }),
        headers: {
            "Content-Type": "application/json"
        }
      })
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
              <div className = "ai-prompt-copy">
                Whether it's leftover ingredients, canned beans you don't know what to do with,
                or a dinner that needs some more inspiration,
                let ChefAI help you come up with a delicious recipe!
              </div>
          </div>
          <form className="thq-card"  onSubmit={(e) => {
            e.preventDefault();
            createNewRecipe();
          }}>
            <div></div>
            <div className="food-form-input1">
              <label htmlFor="contact-form-3-name" className="thq-header-2">
                Do you have any dietary restrictions?
              </label>
              <input
                type="text"
                id="contact-form-3-name"
                placeholder="E.g. vegan, vegetarian, halal...etc."
                rows="Title"
                className="thq-input"
                value={diet_restrictions}
                onChange={(e) => set_diet_restrictions(e.target.value)}
              />
            </div>
            <div className="food-form-input2">
              <label htmlFor="contact-form-3-email" className="thq-body-small">
                How much time do you have?
              </label>
              <input
                type="text"
                id="contact-form-3-email"
                required={true}
                placeholder="15/30/60/120 minutes"
                className="thq-input"
                value={available_time}
                onChange={(e) => set_available_time(e.target.value)}
              />
            </div>
            <div className="food-form-input3">
              <label htmlFor="contact-form-3-email" className="thq-body-small">
                What is your skill level?
              </label>
              <input
                type="text"
                id="contact-form-3-email"
                required={true}
                placeholder="Beginner, Intermediate, Expert?"
                className="thq-input"
                value={skill_level}
                onChange={(e) => set_skill_level(e.target.value)}
              />
            </div>
            <div className="food-form-container">
              <label
                htmlFor="contact-form-3-message"
                className="thq-body-small"
              > What ingredients do you have kicking around?
              </label>
              <textarea
                id="contact-form-3-message"
                rows="3"
                placeholder="E.g. Half a carrot, some onions, shredded cheese..."
                className="thq-input"
                value={ingredients}
                onChange={(e) => set_ingredients(e.target.value)}
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
