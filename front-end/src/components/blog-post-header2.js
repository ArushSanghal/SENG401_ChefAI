import React, { Fragment, useState, useEffect } from 'react'

import PropTypes from 'prop-types'

import './blog-post-header2.css'

const BlogPostHeader2 = (props) => {
  return (
    <div className="blog-post-header2-blog-post-header3 thq-section-padding">
      <div className="blog-post-header2-max-width thq-section-max-width">
        <div className="blog-post-header2-section-title thq-flex-column">
          <div className="blog-post-header2-title thq-flex-column">
            <div className="blog-post-header2-content1">
              <span className="thq-body-small">Blog</span>
              <svg viewBox="0 0 1024 1024" className="thq-icon-small">
                <path d="M426 256l256 256-256 256-60-60 196-196-196-196z"></path>
              </svg>
              <span className="thq-body-small">
                {props.category ?? (
                  <Fragment>
                    <span className="blog-post-header2-text19">
                      Fishing Tips
                    </span>
                  </Fragment>
                )}
              </span>
            </div>
            <div className="blog-post-header2-content2">
              <h1 className="blog-post-header2-text11 thq-heading-1">
                {props.blogPostTitle ?? (
                  <Fragment>
                    <span className="blog-post-header2-text17">
                      Top 10 Fishing Tips for Beginners
                    </span>
                  </Fragment>
                )}
              </h1>
              <div className="blog-post-header2-content3">
                <div className="blog-post-header2-author">
                  <span className="thq-body-small"></span>
                  <span className="thq-body-small">
                    {props.avatarName ?? (
                      <Fragment>
                        <span className="blog-post-header2-text20">
                          John Fisher
                        </span>
                      </Fragment>
                    )}
                  </span>
                </div>
                <div className="blog-post-header2-time">
                  <span className="thq-body-small">
                    {props.date ?? (
                      <Fragment>
                        <span className="blog-post-header2-text16">
                          September 15, 2022
                        </span>
                      </Fragment>
                    )}
                  </span>
                  <span className="thq-body-small">•</span>
                  <span className="thq-body-small">
                    {props.readTime ?? (
                      <Fragment>
                        <span className="blog-post-header2-text18">
                          5 minutes
                        </span>
                      </Fragment>
                    )}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div className="blog-post-header2-container">
          <img
            alt={props.blogPostImageAlt}
            src={props.blogPostImageSrc}
            className="blog-post-header2-image1 thq-img-ratio-4-3"
          />
        </div>
      </div>
    </div>
  )
}

BlogPostHeader2.defaultProps = {
  date: undefined,
  blogPostTitle: undefined,
  readTime: undefined,
  category: undefined,
  avatarName: undefined,
  blogPostImageAlt: 'Fishing tips for beginners',
  blogPostImageSrc: '/images/recipe_card.jpg'
}

BlogPostHeader2.propTypes = {
  date: PropTypes.element,
  blogPostTitle: PropTypes.element,
  readTime: PropTypes.element,
  category: PropTypes.element,
  avatarName: PropTypes.element,
  blogPostImageAlt: PropTypes.string,
  blogPostImageSrc: PropTypes.string,
}


export default BlogPostHeader2
