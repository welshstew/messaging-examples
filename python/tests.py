#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
#

import argparse
import sys
import time

from plano import *

def open_test_session(session):
    set_message_threshold("error")

def test_qpid_jms_connect(session):
    check_connect_usage(jms_prog("Connect"))

    with TestServer() as server:
        call("scripts/run-qpid-jms-example net.ssorj.messaging.examples.jms.Connect {}", server.connection_url)

def test_qpid_jms_send_and_receive(session):
    check_send_usage(jms_prog("Send"))
    check_receive_usage(jms_prog("Receive"))

    with TestServer() as server:
        call("scripts/run-qpid-jms-example net.ssorj.messaging.examples.jms.Send {} examples abc", server.connection_url)
        call("scripts/run-qpid-jms-example net.ssorj.messaging.examples.jms.Receive {} examples 1", server.connection_url)

def test_qpid_proton_cpp_connect(session):
    with TestServer() as server:
        call("qpid-proton-cpp/build/connect {}", server.connection_url)

def test_qpid_proton_cpp_send_and_receive(session):
    with TestServer() as server:
        call("qpid-proton-cpp/build/send {} examples abc", server.connection_url)
        call("qpid-proton-cpp/build/receive {} examples 1", server.connection_url)

def test_qpid_proton_python_connect(session):
    check_connect_usage("qpid-proton-python/connect.py")

    with TestServer() as server:
        call("qpid-proton-python/connect.py {}", server.connection_url)

def test_qpid_proton_python_send_and_receive(session):
    check_send_usage("qpid-proton-python/send.py")
    check_receive_usage("qpid-proton-python/receive.py")

    with TestServer() as server:
        call("qpid-proton-python/send.py {} examples abc", server.connection_url)
        call("qpid-proton-python/receive.py {} examples 1", server.connection_url)

def test_qpid_proton_python_request_and_respond(session):
    check_request_usage("qpid-proton-python/request.py")
    check_respond_usage("qpid-proton-python/respond.py")

    with TestServer() as server:
        with start_process("qpid-proton-python/respond.py {} examples 1", server.connection_url):
            call("qpid-proton-python/request.py {} examples abc", server.connection_url)

def test_rhea_connect(session):
    with TestServer() as server:
        call("rhea/connect.js {}", server.connection_url)

def test_rhea_send_and_receive(session):
    check_send_usage("rhea/send.js")
    check_receive_usage("rhea/receive.js")

    with TestServer() as server:
        call("rhea/send.js {} examples abc", server.connection_url)
        call("rhea/receive.js {} examples 1", server.connection_url)

def test_rhea_request_and_respond(session):
    check_request_usage("rhea/request.js")
    check_respond_usage("rhea/respond.js")

    with TestServer() as server:
        with start_process("rhea/respond.js {} examples 1", server.connection_url):
            call("rhea/request.js {} examples abc", server.connection_url)

class TestServer(object):
    def __init__(self):
        self.port = random_port()
        self.connection_url = "amqp://127.0.0.1:{}".format(self.port)
        self.output_file = make_temp_file()

        self.output = None
        self.proc = None

    def __enter__(self):
        self.output = open(self.output_file, "w")

        self.proc = start_process("scripts/test-broker 127.0.0.1 {0}", self.port, output=self.output)
        self.proc.connection_url = self.connection_url

        time.sleep(0.1) # XXX Ugh

        return self.proc

    def __exit__(self, exc_type, exc_value, traceback):
        stop_process(self.proc)

        self.output.flush()
        self.output.close()

        print("-- Server output --")

        for line in read_lines(self.output_file):
            print("> {}".format(line[:-1]))

# XXX Check for matching program name

def check_connect_usage(command):
    usage = None

    try:
        call_for_stderr(command)
    except CalledProcessError as e:
        usage = e.output

    assert usage, usage
    assert "CONNECTION-URL" in usage, usage

def check_send_usage(command):
    usage = None

    try:
        call_for_stderr(command)
    except CalledProcessError as e:
        usage = e.output

    assert usage, usage
    assert "CONNECTION-URL ADDRESS MESSAGE-BODY" in usage, usage

def check_receive_usage(command):
    usage = None

    try:
        call_for_stderr(command)
    except CalledProcessError as e:
        usage = e.output

    assert usage, usage
    assert "CONNECTION-URL ADDRESS [MESSAGE-COUNT]" in usage, usage

check_request_usage = check_send_usage
check_respond_usage = check_receive_usage

def jms_prog(class_name):
    return "scripts/run-qpid-jms-example net.ssorj.messaging.examples.jms.{}".format(class_name)
