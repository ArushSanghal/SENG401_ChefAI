import React, { Fragment } from 'react'

import PropTypes from 'prop-types'

import './banner11.css'
import { Link } from 'react-router-dom/cjs/react-router-dom'

const Banner11 = (props) => {
  return (
    <div className="banner11-container1 thq-section-padding">
      <div className="banner11-max-width thq-section-max-width">
        <div className="banner11-container2">
          <h2 className="banner11-title thq-heading-2">
            {props.heading1 ?? (
              <Fragment>
                <span className="banner11-text5">Title</span>
              </Fragment>
            )}
          </h2>
          <h3 className="banner11-text1 thq-heading-3">
            {props.content1 ?? (
              <Fragment>
                <span className="banner11-text3">
                  Body
                </span>
              </Fragment>
            )}
          </h3>
        </div>
      </div>
    </div>
  )
}

Banner11.defaultProps = {
    content1: undefined,
    heading1: undefined,
}

Banner11.propTypes = {
    content1: PropTypes.element,
    heading1: PropTypes.element,
}

export default Banner11
