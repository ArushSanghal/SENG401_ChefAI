import React, { Fragment, useEffect, useState } from 'react';
import { useLocation, useHistory } from 'react-router-dom';
import PropTypes from 'prop-types';
import './sign-in1.css';
import { Link } from 'react-router-dom/cjs/react-router-dom';

const SignIn1 = (props) => {
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [members, setMembers] = useState(null);
    const [admins, setAdmins] = useState(null);
    const location = useLocation();
    const [successMessage, setSuccessMessage] = useState("");
    const history = useHistory();

    // Check for success query parameter
    useEffect(() => {
        const queryParams = new URLSearchParams(location.search);
        if (queryParams.get('success') === 'true') {
            setSuccessMessage("Account creation successful.");
        }
    }, [location]);

    function checkCredentials() {
        fetch("http://127.0.0.1:8000/login/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                email: username,
                password: password,
            }),
        })
        .then((response) => response.json())
        .then((data) => {
            console.log("Login Response:", data);
            if (data.access) { // Check if the access token exists
                // Store JWT tokens in localStorage
                localStorage.setItem("access_token", data.access);
                localStorage.setItem("refresh_token", data.refresh);
                console.log("Access Token:", localStorage.getItem("access_token"));
                console.log("Refresh Token:", localStorage.getItem("refresh_token"));
    
                // Redirect to user profile
                alert("Login successful!");
                history.push("/user-profile");
            } else {
                console.log("Details:", data)
                alert("Invalid credentials.");
            }
        })
        .catch((error) => console.log("Fetch error:", error));
    }

    useEffect(() => {
        fetch("http://localhost:3000/members/members", {
            method: "GET",
        })
        .then((response) => response.json())
        .then((data) => {
            setMembers(data);
            console.log(data);
        })
        .catch((error) => console.log(error));
    }, []);

    useEffect(() => {
        fetch("http://localhost:3000/members/admins", {
            method: "GET",
        })
        .then((response) => response.json())
        .then((data) => {
            setAdmins(data);
            console.log(data);
        })
        .catch((error) => console.log(error));
    }, []);

    return (
        <div className="sign-in1-container1 thq-section-padding">
            <div className="sign-in1-max-width thq-section-max-width">
                <div className="sign-in1-form-root">
                    <div className="sign-in1-form1">
                        <div className="sign-in1-title-root">
                            <h2 className="thq-heading-2">
                                {props.heading1 ?? (
                                    <Fragment>
                                        <span className="sign-in1-text20">Sign in</span>
                                    </Fragment>
                                )}
                            </h2>
                            {/* Add a wrapper for success message */}
                            <div className="sign-in1-success-message-wrapper">
                                {successMessage && (
                                    <p className="sign-in1-success-message">
                                        {successMessage}
                                    </p>
                                )}
                            </div>
                        </div>
                        <form className="sign-in1-form2" onSubmit={(e) => {
                            e.preventDefault();
                            checkCredentials();
                        }}>
                            <div className="sign-in1-email">
                                <label htmlFor="thq-sign-in-1-email" className="thq-body-large">
                                    Email
                                </label>
                                <input
                                    id="thq-sign-in-1-email"
                                    required="true"
                                    placeholder="example@email.com"
                                    className="sign-in1-textinput1 thq-input thq-body-large"
                                    value={username}
                                    onChange={(e) => setUsername(e.target.value)}
                                />
                            </div>
                            <div className="sign-in1-password">
                                <div className="sign-in1-container2">
                                    <label
                                        htmlFor="thq-sign-in-1-password"
                                        className="thq-body-large"
                                    >
                                        Password
                                    </label>
                                </div>
                                <input
                                    type="password"
                                    id="thq-sign-in-1-password"
                                    required="true"
                                    placeholder="Password"
                                    className="sign-in1-textinput2 thq-input thq-body-large"
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                />
                            </div>
                            <button
                                type="submit"
                                className="sign-in1-button1 thq-button-filled"
                            >
                                <span className="sign-in1-text14 thq-body-small">
                                    {props.action1 ?? (
                                        <Fragment>
                                            <span className="sign-in1-text22">Sign in</span>
                                        </Fragment>
                                    )}
                                </span>
                            </button>
                        </form>
                        <div className="sign-in1-container3">
                            <div className="sign-in1-container4">
                                <div className="sign-in1-terms-agree">
                                    <p className="thq-body-large">
                                        <span>
                                            By continuing, you agree to the Terms of use and Privacy Policy.
                                        </span>
                                    </p>
                                </div>
                            </div>
                            <div className="sign-in1-container5">
                                <a
                                    href="https://example.com"
                                    target="_blank"
                                    rel="noreferrer noopener"
                                    className="sign-in1-link1 thq-body-small"
                                >
                                    Issues with Sign in
                                </a>
                                <a
                                    href="https://example.com"
                                    target="_blank"
                                    rel="noreferrer noopener"
                                    className="sign-in1-link2 thq-body-small"
                                >
                                    Forgot password
                                </a>
                            </div>
                        </div>
                    </div>
                </div>
                <div className="sign-in1-container6">
                    <div className="sign-in1-divider1">
                        <div className="sign-in1-divider2"></div>
                        <span className="thq-body-large">
                            {props.content1 ?? (
                                <Fragment>
                                    <span className="sign-in1-text23">New to our community</span>
                                </Fragment>
                            )}
                        </span>
                        <div className="sign-in1-divider3"></div>
                    </div>
                    <Link to={props.newAccount}>
                        <button type="button" className="sign-in1-button2 thq-button-outline">
                            <span className="sign-in1-text19 thq-body-small">
                                {props.action2 ?? (
                                    <Fragment>
                                        <span className="sign-in1-text21">Create an account</span>
                                    </Fragment>
                                )}
                            </span>
                        </button>
                    </Link>
                </div>
            </div>
        </div>
    );
}

SignIn1.defaultProps = {
    heading1: undefined,
    action2: undefined,
    action1: undefined,
    content1: undefined,
    newAccount: '/signup'
}

SignIn1.propTypes = {
    heading1: PropTypes.element,
    action2: PropTypes.element,
    action1: PropTypes.element,
    content1: PropTypes.element,
    newAccount: PropTypes.string
}

export default SignIn1;