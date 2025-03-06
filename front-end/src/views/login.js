import React, { Fragment, useState, useEffect } from 'react'

import { Helmet } from 'react-helmet'
import './home.css'
import SignIn1 from '../components/sign-in1'

const Login = (props) => {



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
    <div className="blog-container">
      <Helmet>
        <title>ChefAI</title>
        <meta property="og:title" content="ChefAI" />
      </Helmet>

    <SignIn1
    ></SignIn1>

      
    </div>
  )
}






export default Login
