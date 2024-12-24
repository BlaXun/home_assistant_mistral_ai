<a id="readme-top"></a>
<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>	
    </li>
    <li>
      <a href="#what-is-mistral-ai">What is Mistral AI</a>	
    </li>
    <li>
	<a href="#example-use-cases">Example Use-Cases</a>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li>
	<a href="#usage">Usage</a>
    	<ul>
	  <li><a href="#service">Service</a></li>
	  <li><a href="#event">Event</a></li>
	  <li><a href="#sensor-entity">Sensor Entity</a></li>
	</ul>
    </li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project

This is a custom integration for [Home Assistant](https://www.home-assistant.io/) which allows for sending prompts to [Mistral AI](https://mistral.ai/)
<p align="right">(<a href="#readme-top">back to top</a>)</p>

## What is Mistral AI
Mistral AI is a generative AI created in europe (france). It offers different models of their ai, each specialized for different topics.
This ai had high scores in several benchmarks, even beating previous versions of Chat GPT.
Right now using Mistral AI is free.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Example Use-Cases

<lu>
  <li>Let mistral ai decide wether you should open the windows. Send the outside temperature and humidity to mistral ai along with the avarage temperature and humidity of all your rooms.</li>
  <li>Get dynamic push notifications created by the AI instead of the same static sentences you normall define.</li>
  <li>Feed mistral ai with your workout data to get a quick summary</li>
  <li>Use mistral ai coding model to let it generate jinja + markdown to populate your dashboard</li>
  <li>Generate template sensor code using mistral coding model</li>
</lu>


<!-- GETTING STARTED -->
## Getting Started

Before you can use the integration check the prerequisites. Once thats done, follow up with the installation


### Prerequisites

In order to be able to use this integration you <b>must</b> sign-up with [Mistral AI](https://mistral.ai/). This is currently free!
Once you got your account you can request an API-Key. 
If you wish to use agents you can also define those in the developer portal. Each agent has its unique id which you can use in this integration.

<p align="right">(<a href="#readme-top">back to top</a>)</p>


## Installation

Download the files from this repository and place the <b>mistral_ai_api</b> directory into your <b>custom_components</b> directory.
Next, add the following entry to your <b>configuration.yaml</b>

```yaml
  mistral_ai_api:
    name: "Mistral AI API"
    api_key: !secret mistral_token
  ```

Once that's done add an entry for <b>mistral_token</b> to your <b>secrets.yaml</b>
The token is the token your received from registering with mistral ai.

Now, restart Home Assistant and you should be good to go.


<!-- USAGE EXAMPLES -->
## Usage

The integration offers three key-parts

<lu>
	<li>A service called mistral_ai_api.send_prompt</li>
	<li>An event with the identifier <b>mistral_ai_response</b></li>
	<li>The sensor.mistral_ai_api-Entity</li>
</lu>

### Service

You can call the send_prompt-command like this

```yaml
    action: mistral_ai_api.send_prompt
    metadata: {}
    data:
      prompt: Whats the weather
      identifier: my-question-123
```

Or like this

```yaml
    action: mistral_ai_api.send_prompt
      metadata: {}
        data:
          prompt: Give me a jinja2 template to show some data in a nice formatted way. Make sure to only return the code as-is so I can use it directly in a markdown. Don't add any explanation, just return the code.
          model: codestral-latest
          identifier: my-question-123
          conversation_id: my-conversation
```

This will send the prompt to mistral ai.
Once mistral ai sent back the response the mentioned event will be thrown and the sensor-Entity will get its state and attribute updated.

As you can see the mistral_ai_api.send_prompt takes additional (optional) arguments

<table>
	<tr>
		<td><b>prompt</b></t>
		<td>The prompt to send to mistral</td>
	<tr>
	<tr>
		<td><b>conversation_id</b></t>
		<td><i>optional</i>	If you want to have a real conversation with the model (not just one answer to one prompt and then be done) you need to supply
		a conversation id. This is used as a filename so, please be careful with deciding for a name.</td>
	<tr>
	<tr>
		<td><b>model</b></t>
		<td>The mistral ai model to be used. Not required when using an agent</td>
	<tr>
	<tr>
		<td><b>agent_id</b></t>
		<td><i>optional</i>	The id of an agent you want to utilize</td>
	<tr>
	<tr>
		<td><b>identifier</b></t>
		<td><i>optional</i>	A custom identifier which will be returned in the event so you know which prompt the answer belonged to</td>
	<tr>
	<tr>
		<td><b>timeout</b></t>
		<td><i>optional</i>	Timeout in seconds which defines how long home assistant should wait for an answer before terminating the request. Value of 60 seconds seems fine.</td>
	<tr>
</table>

In addition to this there is another service called "mistral_ai_api.retrieve_last"
This service will return the data for the last communication with mistral ai.
The data consists of the following

<table>
	<tr>
		<td><b>last_prompt</b></t>
		<td>The prompt that was last sent</td>
	<tr>
	<tr>
		<td><b>last_response</b></t>
		<td>The last response returned by mistral</td>
	<tr>
	<tr>
		<td><b>identifier</b></t>
		<td>The last identifier assigned to the communication</td>
	<tr>
	<tr>
		<td><b>timestamp</b></td>
		<td>The last set timestamp</td>
	<tr>
</table>

This example code shows how to use the service action in a script in home assistant

```yaml
    alias: "[Mistral AI] Retrieve last communication"
    sequence:
        - action: mistral_ai_api.retrieve_last
          metadata: {}
          data: {}
          response_variable: result
        - variables:
              identifier: "{{result.identifier}}"
              last_prompt: "{{result.last_prompt}}"
              last_response: "{{result.last_response}}"
              timestamp: "{{result.timestamp}}"
description: "Retrieves the last communication with mistral"
```

### Event
You can react to that in an automation and do whatever you want with the result

```yaml
    alias: "[Mistral AI] React on mistral ai response"
    description: ""
    triggers:
      - trigger: event
        event_type: mistral_ai_response
    conditions: []
    actions:
      - action: notify.mobile_app_iphone_5
        metadata: {}
        data:
          message: >-
            {{trigger.event.data.identifier}} - {{trigger.event.data.agent_id}} -
            {{trigger.event.data.response}}
    mode: single
```

### Sensor Entity

In addition to the event the integration also ships with a Sensor.
The id of the sensor is sensor.mistral_ai_api.
This sensor can have one of two states

<table>
	<tr><td><b>idle</b></td><td>Not doing anything. This is the state it starts with</td></tr>
	<tr><td><b>processing</b>b></td><td>A prompt was sent to mistral ai. Now waiting for the response</td></tr>	
</table>

Given these two states one could create an automation that reacts to the change of the state from <i>idle</i> to <i>processing</i>.

Next up there are a couple of attributes for this entity which are as follows

<table>
	<tr><td><b>last_prompt</b></td><td>The last response that was sent to mistral ai</td></tr>
	<tr><td><b>last_response</b></td><td>The last response from mistral ai</td></tr>
	<tr><td><b>identifier</b></td><td>The last identifier belonging to the prompt and response</td></tr>
	<tr><td><b>timestamp</b></td><td>A timestamp that is refreshed whenever a prompt was sent or a response was received</td></tr>
</table>

<p align="right">(<a href="#readme-top">back to top</a>)</p>
