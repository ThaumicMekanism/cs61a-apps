// @flow strict

import * as React from "react";

import type { State } from "./models";

export default React.createContext<{
  ...State,
  updateState: (State) => void,
}>({
  config: {
    canStudentsChange: true,
    canTutorsChange: true,
    canTutorsReassign: true,
    message: "",
  },
  currentUser: null,
  sections: [],
  history: [],
  taughtSections: [],
  enrolledSection: null,
  updateState: () => {},
});
