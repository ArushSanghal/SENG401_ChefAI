import React, { Fragment, useState } from 'react';
import { useHistory } from "react-router-dom";
import PropTypes from 'prop-types';

import './sign-up2.css';

const SignUp2 = (props) => {
    const history = useHistory();

    const [firstName, setFirstName] = useState("");
    const [lastName, setLastName] = useState("");
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [email, setEmail] = useState("");

    function addNewUser() {
        fetch("http://127.0.0.1:8000/register/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                first_name: firstName,
                last_name: lastName,
                username: username,
                email: email,
                password: password,
            }),
        })
        .then((response) => response.json())
        .then((data) => {
            console.log("Response Data:", data);
            if (data.message && data.message.includes("successfully")) {
                alert("Registration successful! Please log in.");
            } else {
                alert("Error: " + (data.error || data.message));
            }
        })
        .catch((error) => console.log("Fetch error:", error));
    }

    return (
        <div className="sign-up2-container1">
            <div className="sign-up2-max-width thq-section-max-width">
                <div className="sign-up2-container2">
                    <img
                        alt={props.image1Alt}
                        src={props.image1Src}
                        className="sign-up2-sign-up-image thq-img-ratio-4-6"
                    />
                </div>
                <div className="sign-up2-form-root thq-section-padding">
                    <div className="sign-up2-form1">
                        <div className="sign-up2-title-root">
                            <h2 className="thq-heading-2">
                                {props.heading1 ?? (
                                    <Fragment>
                                        <span className="sign-up2-text24">Create an account</span>
                                    </Fragment>
                                )}
                            </h2>
                            <div className="sign-up2-have-an-account-login1">
                                <p className="thq-body-large">
                                    Already have an account? 
                                    <button 
                                        onClick={() => history.push("/")} 
                                        className="sign-in-button"
                                        style={{
                                            background: "none",
                                            border: "none",
                                            color: "blue",
                                            cursor: "pointer",
                                            textDecoration: "underline",
                                            fontSize: "inherit",
                                            marginLeft: "5px"
                                        }}
                                    >
                                        Sign in
                                    </button>
                                </p>
                            </div>
                        </div>
                        <form className="sign-up2-form2" onSubmit={(e) => {
                            e.preventDefault();
                            addNewUser();
                        }}>
                            <div className="sign-up2-first-name">
                                <label htmlFor="thq-sign-up-2-first-name" className="thq-body-large">
                                    First Name
                                </label>
                                <input
                                    type="text"
                                    id="thq-sign-up-2-first-name"
                                    required
                                    placeholder="First Name"
                                    className="sign-up2-textinput1 thq-input thq-body-large"
                                    value={firstName}
                                    onChange={(e) => setFirstName(e.target.value)}
                                />
                            </div>
                            <div className="sign-up2-last-name">
                                <label htmlFor="thq-sign-up-2-last-name" className="thq-body-large">
                                    Last Name
                                </label>
                                <input
                                    type="text"
                                    id="thq-sign-up-2-last-name"
                                    required
                                    placeholder="Last Name"
                                    className="sign-up2-textinput1 thq-input thq-body-large"
                                    value={lastName}
                                    onChange={(e) => setLastName(e.target.value)}
                                />
                            </div>
                            <div className="sign-up2-username">
                                <label htmlFor="thq-sign-up-2-username" className="thq-body-large">
                                    Username
                                </label>
                                <input
                                    type="text"
                                    id="thq-sign-up-2-username"
                                    required
                                    placeholder="Username"
                                    className="sign-up2-textinput1 thq-input thq-body-large"
                                    value={username}
                                    onChange={(e) => setUsername(e.target.value)}
                                />
                            </div>
                            <div className="sign-up2-email">
                                <label htmlFor="thq-sign-up-2-email" className="thq-body-large">
                                    Email
                                </label>
                                <input
                                    type="email"
                                    id="thq-sign-up-2-email"
                                    required
                                    placeholder="Email address"
                                    className="sign-up2-textinput2 thq-input thq-body-large"
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                />
                            </div>
                            <div className="sign-up2-password">
                                <div className="sign-up2-textfield">
                                    <div className="sign-up2-container3">
                                        <label htmlFor="thq-sign-up-2-password" className="thq-body-large">
                                            Password
                                        </label>
                                    </div>
                                    <input
                                        type="password"
                                        id="thq-sign-up-2-password"
                                        required
                                        placeholder="Password"
                                        className="sign-up2-textinput3 thq-input thq-body-large"
                                        value={password}
                                        onChange={(e) => setPassword(e.target.value)}
                                    />
                                </div>
                                <span className="sign-up2-text17 thq-body-small">
                                    {props.content1 ?? (
                                        <Fragment>
                                            <span className="sign-up2-text23">
                                                Use 8 or more characters
                                            </span>
                                        </Fragment>
                                    )}
                                </span>
                            </div>
                            <button type="submit" className="thq-button-filled sign-up2-button">
                                <span className="sign-up2-text21 thq-body-small">
                                    {props.action1 ?? (
                                        <Fragment>
                                            <span className="sign-up2-text25">Create an account</span>
                                        </Fragment>
                                    )}
                                </span>
                            </button>
                        </form>
                        <div className="sign-up2-terms-agree">
                            <p className="thq-body-large">
                                <span>
                                    By creating an account, you agree to the Terms of use and
                                    Privacy Policy.
                                </span>
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

SignUp2.defaultProps = {
    content1: undefined,
    image1Src:
        'https://images.unsplash.com/photo-1500462918059-b1a0cb512f1d?ixid=M3w5MTMyMXwwfDF8c2VhcmNofDM3fHxhYnN0cmFjdHxlbnwwfHx8fDE3MTI5MzE4MzR8MA&ixlib=rb-4.0.3&w=1400',
    heading1: undefined,
    image1Alt: 'SignUp Image',
    action1: undefined,
};

SignUp2.propTypes = {
    content1: PropTypes.element,
    image1Src: PropTypes.string,
    heading1: PropTypes.element,
    image1Alt: PropTypes.string,
    action1: PropTypes.element,
};

export default SignUp2;
