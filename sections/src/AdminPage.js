/* eslint-disable react/no-array-index-key,camelcase */
// @flow strict

import "bootstrap/dist/css/bootstrap.css";
import { useContext, useState } from "react";
import * as React from "react";
import Button from "react-bootstrap/Button";
import Col from "react-bootstrap/Col";
import Tab from "react-bootstrap/Tab";
import Table from "react-bootstrap/Table";
import Tabs from "react-bootstrap/Tabs";
import Form from "react-bootstrap/Form";
import FormControl from "react-bootstrap/FormControl";
import InputGroup from "react-bootstrap/InputGroup";
import Container from "react-bootstrap/Container";
import Row from "react-bootstrap/Row";
import { Redirect } from "react-router-dom";
import StateContext from "./StateContext";
import ToggleSwitch from "./ToggleSwitch";
import useAPI from "./useAPI";

export default function AdminPage(): React.Node {
  const { config, currentUser } = useContext(StateContext);

  const [sheetURL, setSheetURL] = useState("");
  const [studentFile, setStudentFile] = useState(null);
  const [tutorFile, setTutorFile] = useState(null);
  const [importStatus, setImportStatus] = useState("Import");

  const updateConfig = useAPI("update_config");
  const importSections = useAPI("import_sections", (data) => {
    // If data is good
    setImportStatus("Import");
    // Else throw error
  });
  const deleteAllSections = useAPI("delete_all_sections");
  const importAssignments = useAPI("import_assignments");

  const importAssignmentsFromFile = () => {
    setImportStatus("Importing");
    let args = {tutor_file: tutorFile, student_file: studentFile};
    console.log(args);
    importAssignments(args);
    // Run populate_db.py with file
    // Uploaded notif.
  }

  const exportToJSON = () => {

  }

  if (!currentUser?.isStaff) {
    return <Redirect to="/" />;
  }

  return (
    <Container>
      <br />
      <Row>
        <Col>
          <Tabs defaultActiveKey="general">
            <Tab eventKey="general" title="General">
              <Table striped hover>
                <thead>
                  <tr>
                    <th>Option</th>
                    <th>Value</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td>
                      Should students be able to leave their section and join a
                      new one?
                    </td>
                    <td>
                      <ToggleSwitch
                        defaultChecked={config.canStudentsChange}
                        onChange={(can_students_change) => {
                          updateConfig({ can_students_change });
                        }}
                      />
                    </td>
                  </tr>
                  <tr>
                    <td>
                      Should tutors be able to leave their section, or claim new
                      unassigned sections?
                    </td>
                    <td>
                      <ToggleSwitch
                        defaultChecked={config.canTutorsChange}
                        onChange={(can_tutors_change) => {
                          updateConfig({ can_tutors_change });
                        }}
                      />
                    </td>
                  </tr>
                  <tr>
                    <td>
                      Should tutors be able to remove other tutors from their
                      sections?
                    </td>
                    <td>
                      <ToggleSwitch
                        defaultChecked={config.canTutorsReassign}
                        onChange={(can_tutors_reassign) => {
                          updateConfig({ can_tutors_reassign });
                        }}
                      />
                    </td>
                  </tr>
                </tbody>
              </Table>
              <InputGroup>
                <FormControl
                  placeholder="Tutorial Spreadsheet URL"
                  value={sheetURL}
                  onChange={(e) => setSheetURL(e.target.value)}
                />
                <InputGroup.Append>
                  <Button
                    variant="outline-secondary"
                    onClick={() => importSections({ sheet_url: sheetURL })}
                  >
                    Update
                  </Button>
                </InputGroup.Append>
              </InputGroup>
              <p>
                <small>
                  You must share this spreadsheet with the 61A service account{" "}
                  <a href="mailto:secure-links@ok-server.iam.gserviceaccount.com">
                    secure-links@ok-server.iam.gserviceaccount.com
                  </a>
                  .
                </small>
              </p>
              <Button variant="danger" onClick={() => deleteAllSections()}>
                Delete All
              </Button>
            </Tab>
            <Tab eventKey="data" title="Data">
              Import
              <Form>
                <Form.Group>
                  <Form.File label="Student Assignments" onChange={(e) => {
                    const read = new FileReader();
                    read.readAsText(e.target.files[0]);
                    read.onload = () => {
                      setStudentFile(read.result);
                    }
                  }}/>
                  <Form.File label="Tutor Assignments" onChange={(e) => {
                    const read = new FileReader();
                    /* Careful to ensure encoding is correct */
                    read.readAsText(e.target.files[0]);
                    read.onload = () => {
                      setTutorFile(read.result);
                    }
                  }}/>
                </Form.Group>
                <Button onClick={importAssignmentsFromFile}>
                  {importStatus}
                </Button>
              </Form>
              <Form>
                <Button onClick={exportToJSON}>
                  Export
                </Button>
              </Form>
            </Tab>
          </Tabs>
        </Col>
      </Row>
    </Container>
  );
}
