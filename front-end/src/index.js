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
import GuestHome from './views/guest-home'
import UserProfile from './views/user-profile'


import NotFound from './views/not-found'
import Recipegenpage from './views/recipegenpage'
import SavedRecipes from './views/savedrecipes'

const App = () => {

  const [currentUser, setCurrentUser] = useState(null);


  return (
    <Router>
      <Switch>
          <Route component={Login} exact path="/" />
          <Route component={SignUp} exact path="/signup" />
          <Route component={Recipegenpage} exact path="/recipe" />
          <Route component={GuestHome} exact path="/guest"/>
          <Route component={UserProfile} exact path="/user-profile" />
          <Route component={SavedRecipes} exact path ="/saved-recipes"/>
          <Route component={NotFound} path="**" />
          <Redirect to="**" />
      </Switch>
    </Router>
  )

}


ReactDOM.render(<App />, document.getElementById('app'))
