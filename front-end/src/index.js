import React, {Fragment, useState, useEffect} from 'react'
import ReactDOM from 'react-dom'
import {
  BrowserRouter as Router,
  Route,
  Switch,
  Redirect,
} from 'react-router-dom'

import './style.css'
import Login from './views/login'
import SignUp from './views/signup'
import UserProfile from './components/user-profile'


import NotFound from './views/not-found'

const App = () => {

  const [currentUser, setCurrentUser] = useState(null);


  return (
    <Router>
      <Switch>
          <Route component={Login} exact path="/" />
          <Route component={SignUp} exact path="/signup" />
          <Route component={UserProfile} exact path="/user-profile" />
          
          <Route component={NotFound} path="**" />
          <Redirect to="**" />
      </Switch>
    </Router>
  )
  
}


ReactDOM.render(<App />, document.getElementById('app'))
