/* eslint-disable no-param-reassign,dot-notation */
import React, { Component } from "react";
import "bootstrap/dist/css/bootstrap.min.css";
import "bootstrap/dist/js/bootstrap.min.js";

import $ from "jquery";

import StudentView from "./StudentView.js";
import StaffView from "./StaffView.js";
import ExplanationModal from "./ExplanationModal.js";
import LoginButton from "./LoginButton.js";

import "./App.css";

class App extends Component {
  constructor(props) {
    super(props);
    this.state = {
      isStaff: false,
      email: null,
      name: null,
      SID: null,
      students: [],
      success: false,
      data: null,
      lastUpdated: "Unknown",
    };
    this.explanationModalRef = React.createRef();
  }

  componentDidMount() {
    return this.reloadData();
  }

  reloadData = async (target) => {
    const {
      success,
      retry,
      header,
      data,
      isStaff,
      allStudents,
      email,
      name,
      SID,
      lastUpdated,
    } = await $.get("./query/", { target });
    if (!success && retry) {
      this.refresh();
    }

    if (isStaff) {
      this.setState({
        students: allStudents.map(({ Name, Email, SID }) => ({
          text: `${Name} - ${Email} (${SID})`,
          id: Email,
        })),
      });
    }

    this.setState({
      success,
      email,
      name,
      SID,
      lastUpdated,
      data: { header, data },
      isStaff,
    });
  };

  refresh = () => {
    window.location.replace("./oauth/login");
  };

  handleExplanationClick = () => {
    if (window.EXPLANATION_IS_LINK) {
      window.open(window.EXPLANATION, "__blank");
    } else {
      $(this.explanationModalRef.current).modal();
    }
  };

  render() {
    const contents = !this.state.success ? (
      <LoginButton onClick={this.refresh} />
    ) : this.state.isStaff ? (
      <StaffView onSubmit={this.reloadData} students={this.state.students} />
    ) : (
      <StudentView {...this.state.data} />
    );

    return (
      <>
        <div className="App container">
          <div className="row">
            <div className="col">
              <br />
              <h1 className="display-4">
                <a href="/" style={{ color: "black", textDecoration: "none" }}>
                  <strong>{window.COURSE_CODE}</strong> Status Check
                </a>
              </h1>
            </div>
            <div className="col-auto">
              <br />
              <p className="text-right">
                Logged in as {this.state.name}
                {" ("}
                {this.state.email}
                {")."}
                <br />
                {this.state.SID && `SID: ${this.state.SID}`}
                {this.state.SID && <br />}
                <a href="#" onClick={this.handleExplanationClick}>
                  Grade Explanation
                </a>
              </p>
            </div>
          </div>{" "}
          <div className="row">
            <div className="col">{contents}</div>
          </div>
        </div>
        <footer className="footer mt-auto py-3">
          <div className="container">
            <span className="text-muted">
              Last updated: {this.state.lastUpdated}
            </span>
          </div>
        </footer>

        <ExplanationModal ref={this.explanationModalRef} />
      </>
    );
  }
}

export default App;
