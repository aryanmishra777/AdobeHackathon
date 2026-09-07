# platform.claude.com Documentation (Part 11 of 35)

## Next steps

Source: https://platform.claude.com/llms-full.txt#next-steps-54

<CardGroup cols={2}>
  <Card title="Agent Skills" icon="stack" href="https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview">
    Agent Skills are modular capabilities that extend Claude's functionality. Each Skill packages instructions, metadata, and optional resources (scripts, templates) that Claude uses automatically when relevant.
  </Card>

  <Card title="Computer use tool" icon="computer" href="https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool">
    Give Claude screenshot, mouse, and keyboard control of a desktop environment with the computer use tool.
  </Card>

  <Card title="PDF support" icon="file" href="https://platform.claude.com/docs/en/build-with-claude/pdf-support">
    Process PDFs with Claude. Extract text, analyze charts, and understand visual content from your documents.
  </Card>

  <Card title="Token counting" icon="calculator" href="https://platform.claude.com/docs/en/build-with-claude/token-counting">
    Count the tokens in a message before you send it to Claude. Use token counts to manage rate limits and costs, make model routing decisions, and fit prompts to a target length.
  </Card>
</CardGroup>


---
title: Vision
url: https://platform.claude.com/docs/en/build-with-claude/vision
description: Claude's vision capabilities allow it to understand and analyze images, opening up exciting possibilities for multimodal interaction.
---

This guide describes how to send images to Claude, the limits and costs that apply, and where to find guidance for [coordinate-based workflows](https://platform.claude.com/docs/en/build-with-claude/vision-coordinates).

***


## Send images to Claude

Source: https://platform.claude.com/llms-full.txt#send-images-to-claude

Use Claude's vision capabilities through:

* [claude.ai](https://claude.ai/). Upload an image like you would a file, or drag and drop an image directly into the chat window.
* [Playground](https://platform.claude.com/playground) in the Claude Console. Add images directly to any User message block.
* API request. See the following examples.

On the API, provide images to Claude as `image` content blocks using one of three source types:

1. A base64-encoded image embedded in the request body
2. A URL reference to an image hosted online
3. A `file_id` returned by the [Files API](https://platform.claude.com/docs/en/build-with-claude/files) (upload once, reference many times)

<Note>
  On Amazon Bedrock and Google Cloud, only base64-encoded sources are currently available.
</Note>

<Tip>
  Just as [placing long documents before your query](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices#long-context-prompting) improves results in text prompts, Claude works best when images come before text. Images placed after text or interpolated with text still perform well, but if your use case allows it, prefer an image-then-text structure.
</Tip>

### Base64-encoded image example

<CodeGroup>
  ```bash cURL
  curl https://api.anthropic.com/v1/messages \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "content-type: application/json" \
    -d @- <<EOF
  {
    "model": "claude-opus-5",
    "max_tokens": 1024,
    "messages": [
      {
        "role": "user",
        "content": [
          {
            "type": "image",
            "source": {
              "type": "base64",
              "media_type": "image/jpeg",
              "data": "$BASE64_IMAGE_DATA"
            }
          },
          {
            "type": "text",
            "text": "Describe this image."
          }
        ]
      }
    ]
  }
  EOF

bash CLI
  curl -sSo ./vision-example.jpg \
    https://platform.claude.com/docs/images/vision-example.jpg

  ant messages create <<'YAML'
  model: claude-opus-5
  max_tokens: 1024
  messages:
    - role: user
      content:
        - type: image
          source:
            type: base64
            media_type: image/jpeg
            data: "@./vision-example.jpg"
        - type: text
          text: Describe this image.
  YAML

python Python
  image1_data = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAIAAACQd1PeAAAADElEQVR4nGP4z8AAAAMBAQDJ/pLvAAAAAElFTkSuQmCC"
  image1_media_type = "image/png"

  client = anthropic.Anthropic()
  message = client.messages.create(
      model="claude-opus-5",
      max_tokens=1024,
      messages=[
          {
              "role": "user",
              "content": [
                  {
                      "type": "image",
                      "source": {
                          "type": "base64",
                          "media_type": image1_media_type,
                          "data": image1_data,
                      },
                  },
                  {"type": "text", "text": "Describe this image."},
              ],
          }
      ],
  )
  print(message)

typescript TypeScript
  const anthropic = new Anthropic();

  const message = await anthropic.messages.create({
    model: "claude-opus-5",
    max_tokens: 1024,
    messages: [
      {
        role: "user",
        content: [
          {
            type: "image",
            source: {
              type: "base64",
              media_type: "image/jpeg",
              data: imageData // Base64-encoded image data as string
            }
          },
          {
            type: "text",
            text: "Describe this image."
          }
        ]
      }
    ]
  });

  console.log(message);

csharp C#
  using System.Collections.Generic;
  using Anthropic;
  using Anthropic.Models.Messages;

  AnthropicClient client = new();

  string imageData = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAIAAACQd1PeAAAADElEQVR4nGP4z8AAAAMBAQDJ/pLvAAAAAElFTkSuQmCC";

  var message = await client.Messages.Create(new MessageCreateParams
  {
      Model = Model.ClaudeOpus5,
      MaxTokens = 1024,
      Messages =
      [
          new()
          {
              Role = Role.User,
              Content = new MessageParamContent(new List<ContentBlockParam>
              {
                  new ContentBlockParam(new ImageBlockParam(
                      new ImageBlockParamSource(new Base64ImageSource()
                      {
                          Data = imageData,
                          MediaType = MediaType.ImagePng,
                      })
                  )),
                  new ContentBlockParam(new TextBlockParam("Describe this image.")),
              }),
          }
      ]
  });

  Console.WriteLine(message);

go Go
  client := anthropic.NewClient()

  imageData := "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAIAAACQd1PeAAAADElEQVR4nGP4z8AAAAMBAQDJ/pLvAAAAAElFTkSuQmCC"

  message, err := client.Messages.New(context.TODO(), anthropic.MessageNewParams{
  	Model:     anthropic.ModelClaudeOpus5,
  	MaxTokens: 1024,
  	Messages: []anthropic.MessageParam{
  		anthropic.NewUserMessage(
  			anthropic.NewImageBlockBase64("image/png", imageData),
  			anthropic.NewTextBlock("Describe this image."),
  		),
  	},
  })
  if err != nil {
  	log.Fatal(err)
  }

  fmt.Println(message)

java Java
  AnthropicClient client = AnthropicOkHttpClient.fromEnv();
  String imageData =
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAIAAACQd1PeAAAADElEQVR4nGP4z8AAAAMBAQDJ/pLvAAAAAElFTkSuQmCC";

  List<ContentBlockParam> contentBlockParams = List.of(
    ContentBlockParam.ofImage(
      ImageBlockParam.builder()
        .source(
          Base64ImageSource.builder()
            .mediaType(Base64ImageSource.MediaType.IMAGE_PNG)
            .data(imageData)
            .build()
        )
        .build()
    ),
    ContentBlockParam.ofText(TextBlockParam.builder().text("Describe this image.").build())
  );
  Message message = client
    .messages()
    .create(
      MessageCreateParams.builder()
        .model(Model.CLAUDE_OPUS_5)
        .maxTokens(1024)
        .addUserMessageOfBlockParams(contentBlockParams)
        .build()
    );

  IO.println(message);

php PHP
  $client = new Client();

  $imageData = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAIAAACQd1PeAAAADElEQVR4nGP4z8AAAAMBAQDJ/pLvAAAAAElFTkSuQmCC";

  $message = $client->messages->create(
      maxTokens: 1024,
      messages: [
          [
              'role' => 'user',
              'content' => [
                  [
                      'type' => 'image',
                      'source' => [
                          'type' => 'base64',
                          'media_type' => 'image/png',
                          'data' => $imageData,
                      ],
                  ],
                  ['type' => 'text', 'text' => 'Describe this image.'],
              ],
          ],
      ],
      model: 'claude-opus-5',
  );

  echo json_encode($message, JSON_PRETTY_PRINT), PHP_EOL;

ruby Ruby
  client = Anthropic::Client.new

  image_data = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAIAAACQd1PeAAAADElEQVR4nGP4z8AAAAMBAQDJ/pLvAAAAAElFTkSuQmCC"

  message = client.messages.create(
    model: "claude-opus-5",
    max_tokens: 1024,
    messages: [
      {
        role: "user",
        content: [
          {
            type: "image",
            source: {
              type: "base64",
              media_type: "image/png",
              data: image_data
            }
          },
          { type: "text", text: "Describe this image." }
        ]
      }
    ]
  )

  puts message

bash cURL
  curl https://api.anthropic.com/v1/messages \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "content-type: application/json" \
    -d '{
      "model": "claude-opus-5",
      "max_tokens": 1024,
      "messages": [
        {
          "role": "user",
          "content": [
            {
              "type": "image",
              "source": {
                "type": "url",
                "url": "https://platform.claude.com/docs/images/vision-example.jpg"
              }
            },
            {
              "type": "text",
              "text": "Describe this image."
            }
          ]
        }
      ]
    }'

bash CLI
  ant messages create <<'YAML'
  model: claude-opus-5
  max_tokens: 1024
  messages:
    - role: user
      content:
        - type: image
          source:
            type: url
            url: https://platform.claude.com/docs/images/vision-example.jpg
        - type: text
          text: Describe this image.
  YAML

python Python
  client = anthropic.Anthropic()
  message = client.messages.create(
      model="claude-opus-5",
      max_tokens=1024,
      messages=[
          {
              "role": "user",
              "content": [
                  {
                      "type": "image",
                      "source": {
                          "type": "url",
                          "url": "https://platform.claude.com/docs/images/vision-example.jpg",
                      },
                  },
                  {"type": "text", "text": "Describe this image."},
              ],
          }
      ],
  )
  print(message)

typescript TypeScript
  const anthropic = new Anthropic();

  const message = await anthropic.messages.create({
    model: "claude-opus-5",
    max_tokens: 1024,
    messages: [
      {
        role: "user",
        content: [
          {
            type: "image",
            source: {
              type: "url",
              url: "https://platform.claude.com/docs/images/vision-example.jpg"
            }
          },
          {
            type: "text",
            text: "Describe this image."
          }
        ]
      }
    ]
  });

  console.log(message);

csharp C#
  using System.Collections.Generic;
  using Anthropic;
  using Anthropic.Models.Messages;

  AnthropicClient client = new();

  var message = await client.Messages.Create(new MessageCreateParams
  {
      Model = Model.ClaudeOpus5,
      MaxTokens = 1024,
      Messages =
      [
          new()
          {
              Role = Role.User,
              Content = new MessageParamContent(new List<ContentBlockParam>
              {
                  new ContentBlockParam(new ImageBlockParam(
                      new ImageBlockParamSource(new UrlImageSource()
                      {
                          Url = "https://platform.claude.com/docs/images/vision-example.jpg",
                      })
                  )),
                  new ContentBlockParam(new TextBlockParam("Describe this image.")),
              }),
          }
      ]
  });

  Console.WriteLine(message);

go Go
  client := anthropic.NewClient()

  message, err := client.Messages.New(context.TODO(), anthropic.MessageNewParams{
  	Model:     anthropic.ModelClaudeOpus5,
  	MaxTokens: 1024,
  	Messages: []anthropic.MessageParam{
  		anthropic.NewUserMessage(
  			anthropic.NewImageBlock(anthropic.URLImageSourceParam{
  				URL: "https://platform.claude.com/docs/images/vision-example.jpg",
  			}),
  			anthropic.NewTextBlock("Describe this image."),
  		),
  	},
  })
  if err != nil {
  	log.Fatal(err)
  }

  fmt.Println(message)

java Java
  AnthropicClient client = AnthropicOkHttpClient.fromEnv();

  List<ContentBlockParam> contentBlockParams = List.of(
    ContentBlockParam.ofImage(
      ImageBlockParam.builder()
        .source(
          UrlImageSource.builder()
            .url("https://platform.claude.com/docs/images/vision-example.jpg")
            .build()
        )
        .build()
    ),
    ContentBlockParam.ofText(TextBlockParam.builder().text("Describe this image.").build())
  );
  Message message = client
    .messages()
    .create(
      MessageCreateParams.builder()
        .model(Model.CLAUDE_OPUS_5)
        .maxTokens(1024)
        .addUserMessageOfBlockParams(contentBlockParams)
        .build()
    );
  System.out.println(message);

php PHP
  $client = new Client();

  $message = $client->messages->create(
      maxTokens: 1024,
      messages: [
          [
              'role' => 'user',
              'content' => [
                  [
                      'type' => 'image',
                      'source' => [
                          'type' => 'url',
                          'url' => 'https://platform.claude.com/docs/images/vision-example.jpg',
                      ],
                  ],
                  ['type' => 'text', 'text' => 'Describe this image.'],
              ],
          ],
      ],
      model: 'claude-opus-5',
  );

  echo json_encode($message, JSON_PRETTY_PRINT), PHP_EOL;

ruby Ruby
  client = Anthropic::Client.new

  message = client.messages.create(
    model: "claude-opus-5",
    max_tokens: 1024,
    messages: [
      {
        role: "user",
        content: [
          {
            type: "image",
            source: {
              type: "url",
              url: "https://platform.claude.com/docs/images/vision-example.jpg"
            }
          },
          { type: "text", text: "Describe this image." }
        ]
      }
    ]
  )

  puts message

bash cURL
  # First, upload your image to the Files API
  FILE_ID=$(curl -sS -X POST https://api.anthropic.com/v1/files \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -F "file=@vision-example.jpg" | jq -r '.id')

  # Then use the returned file_id in your message
  curl https://api.anthropic.com/v1/messages \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "content-type: application/json" \
    -d @- <<EOF
  {
    "model": "claude-opus-5",
    "max_tokens": 1024,
    "messages": [
      {
        "role": "user",
        "content": [
          {
            "type": "image",
            "source": {
              "type": "file",
              "file_id": "$FILE_ID"
            }
          },
          {
            "type": "text",
            "text": "Describe this image."
          }
        ]
      }
    ]
  }
  EOF

bash CLI
  curl -sSo vision-example.jpg \
    https://platform.claude.com/docs/images/vision-example.jpg

  # First, upload your image to the Files API
  FILE_ID=$(ant files upload \
    --file ./vision-example.jpg \
    --transform id --raw-output)

  # Then use the returned file_id in your message
  ant messages create \
    --transform content --format yaml <<YAML
  model: claude-opus-5
  max_tokens: 1024
  messages:
    - role: user
      content:
        - type: image
          source:
            type: file
            file_id: $FILE_ID
        - type: text
          text: Describe this image.
  YAML

python Python
  client = anthropic.Anthropic()

  # Upload the image file
  with open("vision-example.jpg", "rb") as f:
      file_upload = client.files.upload(file=("vision-example.jpg", f, "image/jpeg"))

  # Use the uploaded file in a message
  message = client.messages.create(
      model="claude-opus-5",
      max_tokens=1024,
      messages=[
          {
              "role": "user",
              "content": [
                  {
                      "type": "image",
                      "source": {"type": "file", "file_id": file_upload.id},
                  },
                  {"type": "text", "text": "Describe this image."},
              ],
          }
      ],
  )

  print(message.content)

typescript TypeScript
  import Anthropic, { toFile } from "@anthropic-ai/sdk";
  import fs from "node:fs";

  const anthropic = new Anthropic();

  // Upload the image file
  const fileUpload = await anthropic.files.upload({
    file: await toFile(fs.createReadStream("vision-example.jpg"), undefined, {
      type: "image/jpeg"
    })
  });

  // Use the uploaded file in a message
  const response = await anthropic.messages.create({
    model: "claude-opus-5",
    max_tokens: 1024,
    messages: [
      {
        role: "user",
        content: [
          {
            type: "image",
            source: {
              type: "file",
              file_id: fileUpload.id
            }
          },
          {
            type: "text",
            text: "Describe this image."
          }
        ]
      }
    ]
  });

  console.log(response);

csharp C#
  using System.Collections.Generic;
  using Anthropic;
  using Anthropic.Core;
  using Anthropic.Models.Files;
  using Anthropic.Models.Messages;

  AnthropicClient client = new();

  // Upload the image file
  var fileUpload = await client.Files.Upload(new FileUploadParams
  {
      File = new BinaryContent
      {
          Stream = File.OpenRead("vision-example.jpg"),
          FileName = "vision-example.jpg",
          ContentType = new("image/jpeg"),
      },
  });

  // Use the uploaded file in a message
  var response = await client.Messages.Create(new MessageCreateParams
  {
      Model = Model.ClaudeOpus5,
      MaxTokens = 1024,
      Messages =
      [
          new()
          {
              Role = Role.User,
              Content = new MessageParamContent(new List<ContentBlockParam>
              {
                  new ContentBlockParam(new ImageBlockParam(
                      new ImageBlockParamSource(new FileImageSource(fileUpload.ID))
                  )),
                  new ContentBlockParam(new TextBlockParam("Describe this image.")),
              }),
          }
      ]
  });

  Console.WriteLine(response);

go Go
  client := anthropic.NewClient()

  // Upload the image file
  file, err := os.Open("vision-example.jpg")
  if err != nil {
  	log.Fatal(err)
  }
  defer file.Close()

  fileUpload, err := client.Files.Upload(context.Background(),
  	anthropic.FileUploadParams{
  		File: anthropic.File(file, "vision-example.jpg", "image/jpeg"),
  	})
  if err != nil {
  	log.Fatal(err)
  }

  // Use the uploaded file in a message
  message, err := client.Messages.New(context.Background(),
  	anthropic.MessageNewParams{
  		Model:     anthropic.ModelClaudeOpus5,
  		MaxTokens: 1024,
  		Messages: []anthropic.MessageParam{
  			anthropic.NewUserMessage(
  				anthropic.NewImageBlock(anthropic.FileImageSourceParam{
  					FileID: fileUpload.ID,
  				}),
  				anthropic.NewTextBlock("Describe this image."),
  			),
  		},
  	})
  if err != nil {
  	log.Fatal(err)
  }

  fmt.Println(message.Content)

java Java
  import com.anthropic.core.MultipartField;
  import com.anthropic.models.files.FileMetadata;
  import com.anthropic.models.files.FileUploadParams;
  // ...
      AnthropicClient client = AnthropicOkHttpClient.fromEnv();

      // Upload the image file
      FileMetadata file = client.files().upload(
        FileUploadParams.builder()
          .file(
            MultipartField.<InputStream>builder()
              .value(Files.newInputStream(Path.of("vision-example.jpg")))
              .filename("vision-example.jpg")
              .contentType("image/jpeg")
              .build()
          )
          .build()
      );

      // Use the uploaded file in a message
      ImageBlockParam imageParam = ImageBlockParam.builder().fileSource(file.id()).build();

      MessageCreateParams params = MessageCreateParams.builder()
        .model(Model.CLAUDE_OPUS_5)
        .maxTokens(1024)
        .addUserMessageOfBlockParams(
          List.of(
            ContentBlockParam.ofImage(imageParam),
            ContentBlockParam.ofText(
              TextBlockParam.builder().text("Describe this image.").build()
            )
          )
        )
        .build();

      Message message = client.messages().create(params);
      System.out.println(message.content());

php PHP
  use Anthropic\Core\FileParam;

  $client = new Client();

  // Upload the image file
  $fileUpload = $client->files->upload(
      file: FileParam::fromResource(fopen('vision-example.jpg', 'rb'), contentType: 'image/jpeg'),
  );

  // Use the uploaded file in a message
  $message = $client->messages->create(
      maxTokens: 1024,
      messages: [
          [
              'role' => 'user',
              'content' => [
                  [
                      'type' => 'image',
                      'source' => ['type' => 'file', 'fileID' => $fileUpload->id],
                  ],
                  ['type' => 'text', 'text' => 'Describe this image.'],
              ],
          ],
      ],
      model: 'claude-opus-5',
  );

  echo json_encode($message, JSON_PRETTY_PRINT), PHP_EOL;

ruby Ruby
  client = Anthropic::Client.new

  # Upload the image file
  file_upload = client.files.upload(
    file: Anthropic::FilePart.new(
      File.open("vision-example.jpg", "rb"),
      content_type: "image/jpeg"
    )
  )

  # Use the uploaded file in a message
  message = client.messages.create(
    model: "claude-opus-5",
    max_tokens: 1024,
    messages: [
      {
        role: "user",
        content: [
          {
            type: "image",
            source: { type: "file", file_id: file_upload.id }
          },
          { type: "text", text: "Describe this image." }
        ]
      }
    ]
  )

  puts message.content

bash cURL
  curl https://api.anthropic.com/v1/messages \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "content-type: application/json" \
    -d '{
      "model": "claude-opus-5",
      "max_tokens": 1024,
      "messages": [
        {
          "role": "user",
          "content": [
            {
              "type": "text",
              "text": "Image 1:"
            },
            {
              "type": "image",
              "source": {
                "type": "base64",
                "media_type": "image/png",
                "data": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAIAAACQd1PeAAAADElEQVR4nGP4z8AAAAMBAQDJ/pLvAAAAAElFTkSuQmCC"
              }
            },
            {
              "type": "text",
              "text": "Image 2:"
            },
            {
              "type": "image",
              "source": {
                "type": "base64",
                "media_type": "image/png",
                "data": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAIAAACQd1PeAAAADElEQVR4nGNgYPgPAAEDAQAIicLsAAAAAElFTkSuQmCC"
              }
            },
            {
              "type": "text",
              "text": "How are these images different?"
            }
          ]
        }
      ]
    }'

bash CLI
  ant messages create <<'YAML'
  model: claude-opus-5
  max_tokens: 1024
  messages:
    - role: user
      content:
        - type: text
          text: "Image 1:"
        - type: image
          source:
            type: base64
            media_type: image/png
            data: iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAIAAACQd1PeAAAADElEQVR4nGP4z8AAAAMBAQDJ/pLvAAAAAElFTkSuQmCC
        - type: text
          text: "Image 2:"
        - type: image
          source:
            type: base64
            media_type: image/png
            data: iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAIAAACQd1PeAAAADElEQVR4nGNgYPgPAAEDAQAIicLsAAAAAElFTkSuQmCC
        - type: text
          text: How are these images different?
  YAML

python Python
  image1_data = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAIAAACQd1PeAAAADElEQVR4nGP4z8AAAAMBAQDJ/pLvAAAAAElFTkSuQmCC"
  image2_data = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAIAAACQd1PeAAAADElEQVR4nGNgYPgPAAEDAQAIicLsAAAAAElFTkSuQmCC"

  client = anthropic.Anthropic()
  message = client.messages.create(
      model="claude-opus-5",
      max_tokens=1024,
      messages=[
          {
              "role": "user",
              "content": [
                  {"type": "text", "text": "Image 1:"},
                  {
                      "type": "image",
                      "source": {
                          "type": "base64",
                          "media_type": "image/png",
                          "data": image1_data,
                      },
                  },
                  {"type": "text", "text": "Image 2:"},
                  {
                      "type": "image",
                      "source": {
                          "type": "base64",
                          "media_type": "image/png",
                          "data": image2_data,
                      },
                  },
                  {"type": "text", "text": "How are these images different?"},
              ],
          }
      ],
  )
  print(message)

typescript TypeScript
  const anthropic = new Anthropic();

  const image1Data =
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAIAAACQd1PeAAAADElEQVR4nGP4z8AAAAMBAQDJ/pLvAAAAAElFTkSuQmCC";
  const image2Data =
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAIAAACQd1PeAAAADElEQVR4nGNgYPgPAAEDAQAIicLsAAAAAElFTkSuQmCC";

  const message = await anthropic.messages.create({
    model: "claude-opus-5",
    max_tokens: 1024,
    messages: [
      {
        role: "user",
        content: [
          {
            type: "text",
            text: "Image 1:"
          },
          {
            type: "image",
            source: {
              type: "base64",
              media_type: "image/png",
              data: image1Data
            }
          },
          {
            type: "text",
            text: "Image 2:"
          },
          {
            type: "image",
            source: {
              type: "base64",
              media_type: "image/png",
              data: image2Data
            }
          },
          {
            type: "text",
            text: "How are these images different?"
          }
        ]
      }
    ]
  });

  console.log(message);

csharp C#
  AnthropicClient client = new();

  string image1Data = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAIAAACQd1PeAAAADElEQVR4nGP4z8AAAAMBAQDJ/pLvAAAAAElFTkSuQmCC";
  string image2Data = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAIAAACQd1PeAAAADElEQVR4nGNgYPgPAAEDAQAIicLsAAAAAElFTkSuQmCC";

  var message = await client.Messages.Create(new MessageCreateParams
  {
      Model = Model.ClaudeOpus5,
      MaxTokens = 1024,
      Messages =
      [
          new()
          {
              Role = Role.User,
              Content = new MessageParamContent(new List<ContentBlockParam>
              {
                  new ContentBlockParam(new TextBlockParam("Image 1:")),
                  new ContentBlockParam(new ImageBlockParam(
                      new ImageBlockParamSource(new Base64ImageSource()
                      {
                          Data = image1Data,
                          MediaType = MediaType.ImagePng,
                      })
                  )),
                  new ContentBlockParam(new TextBlockParam("Image 2:")),
                  new ContentBlockParam(new ImageBlockParam(
                      new ImageBlockParamSource(new Base64ImageSource()
                      {
                          Data = image2Data,
                          MediaType = MediaType.ImagePng,
                      })
                  )),
                  new ContentBlockParam(new TextBlockParam("How are these images different?")),
              }),
          }
      ]
  });

  Console.WriteLine(message);

go Go
  client := anthropic.NewClient()

  image1Data := "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAIAAACQd1PeAAAADElEQVR4nGP4z8AAAAMBAQDJ/pLvAAAAAElFTkSuQmCC"
  image2Data := "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAIAAACQd1PeAAAADElEQVR4nGNgYPgPAAEDAQAIicLsAAAAAElFTkSuQmCC"

  message, err := client.Messages.New(context.TODO(), anthropic.MessageNewParams{
  	Model:     anthropic.ModelClaudeOpus5,
  	MaxTokens: 1024,
  	Messages: []anthropic.MessageParam{
  		anthropic.NewUserMessage(
  			anthropic.NewTextBlock("Image 1:"),
  			anthropic.NewImageBlockBase64("image/png", image1Data),
  			anthropic.NewTextBlock("Image 2:"),
  			anthropic.NewImageBlockBase64("image/png", image2Data),
  			anthropic.NewTextBlock("How are these images different?"),
  		),
  	},
  })
  if err != nil {
  	log.Fatal(err)
  }

  fmt.Println(message)

java Java
  AnthropicClient client = AnthropicOkHttpClient.fromEnv();

  String image1Data = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAIAAACQd1PeAAAADElEQVR4nGP4z8AAAAMBAQDJ/pLvAAAAAElFTkSuQmCC";
  String image2Data = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAIAAACQd1PeAAAADElEQVR4nGNgYPgPAAEDAQAIicLsAAAAAElFTkSuQmCC";

  List<ContentBlockParam> contentBlockParams = List.of(
      ContentBlockParam.ofText(TextBlockParam.builder().text("Image 1:").build()),
      ContentBlockParam.ofImage(
          ImageBlockParam.builder()
              .source(
                  Base64ImageSource.builder()
                      .mediaType(Base64ImageSource.MediaType.IMAGE_PNG)
                      .data(image1Data)
                      .build()
              )
              .build()
      ),
      ContentBlockParam.ofText(TextBlockParam.builder().text("Image 2:").build()),
      ContentBlockParam.ofImage(
          ImageBlockParam.builder()
              .source(
                  Base64ImageSource.builder()
                      .mediaType(Base64ImageSource.MediaType.IMAGE_PNG)
                      .data(image2Data)
                      .build()
              )
              .build()
      ),
      ContentBlockParam.ofText(
          TextBlockParam.builder().text("How are these images different?").build()
      )
  );

  Message message = client
      .messages()
      .create(
          MessageCreateParams.builder()
              .model(Model.CLAUDE_OPUS_5)
              .maxTokens(1024)
              .addUserMessageOfBlockParams(contentBlockParams)
              .build()
      );

  IO.println(message);

php PHP
  $client = new Client();

  $image1Data = 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAIAAACQd1PeAAAADElEQVR4nGP4z8AAAAMBAQDJ/pLvAAAAAElFTkSuQmCC';
  $image2Data = 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAIAAACQd1PeAAAADElEQVR4nGNgYPgPAAEDAQAIicLsAAAAAElFTkSuQmCC';

  $message = $client->messages->create(
      maxTokens: 1024,
      messages: [
          [
              'role' => 'user',
              'content' => [
                  ['type' => 'text', 'text' => 'Image 1:'],
                  [
                      'type' => 'image',
                      'source' => [
                          'type' => 'base64',
                          'media_type' => 'image/png',
                          'data' => $image1Data,
                      ],
                  ],
                  ['type' => 'text', 'text' => 'Image 2:'],
                  [
                      'type' => 'image',
                      'source' => [
                          'type' => 'base64',
                          'media_type' => 'image/png',
                          'data' => $image2Data,
                      ],
                  ],
                  ['type' => 'text', 'text' => 'How are these images different?'],
              ],
          ],
      ],
      model: 'claude-opus-5',
  );

  echo $message;

ruby Ruby
  client = Anthropic::Client.new

  image1_data = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAIAAACQd1PeAAAADElEQVR4nGP4z8AAAAMBAQDJ/pLvAAAAAElFTkSuQmCC"
  image2_data = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAIAAACQd1PeAAAADElEQVR4nGNgYPgPAAEDAQAIicLsAAAAAElFTkSuQmCC"

  message = client.messages.create(
    model: "claude-opus-5",
    max_tokens: 1024,
    messages: [
      {
        role: "user",
        content: [
          { type: "text", text: "Image 1:" },
          {
            type: "image",
            source: {
              type: "base64",
              media_type: "image/png",
              data: image1_data
            }
          },
          { type: "text", text: "Image 2:" },
          {
            type: "image",
            source: {
              type: "base64",
              media_type: "image/png",
              data: image2_data
            }
          },
          { type: "text", text: "How are these images different?" }
        ]
      }
    ]
  )

  puts message
  ```
</CodeGroup>

In a multi-turn conversation, add new images in later `user` turns the same way. Claude has access to every image from earlier turns, so follow-up questions such as "Are these similar to the first two?" work without including the earlier images again in the new turn's content.

***


## Image limits and costs

Source: https://platform.claude.com/llms-full.txt#image-limits-and-costs

### Request limits

The maximum number of images per message or request is:

* 20 per message on [claude.ai](https://claude.ai/).
* 100 per request on the API, for models with a 200k-token context window.
* 600 per request on the API, for all other models.

The maximum dimensions per image are 8000x8000 px.

If a single API request contains more than 20 images, a stricter per-image dimension limit applies to every image in that request. All `image` blocks in the request count toward this threshold, including images from earlier conversation turns that you resend and images nested inside `tool_result` content (for example, screenshots returned to the computer use tool). On Amazon Bedrock and Google Cloud, document blocks such as PDFs also count toward this threshold. Images exceeding the stricter limit are rejected with an `invalid_request_error` whose message references "many-image requests" and states the current limit in pixels. To stay under the limit on all platforms, either resize each image so that neither dimension exceeds 2000 px, or keep the request to 20 or fewer image and document blocks.

The maximum size per image is:

* 10 MB (base64-encoded) when using the Claude API directly.
* 5 MB (base64-encoded) on Amazon Bedrock and Google Cloud.
* 10 MB on [claude.ai](https://claude.ai/).

<Note>
  Although the API supports up to 600 images per request, [request size limits](https://platform.claude.com/docs/en/api/overview#request-size-limits) (32 MB for standard endpoints; lower on some partner-operated platforms, for example, Amazon Bedrock and Google Cloud) can be reached first. For many images, consider uploading with the [Files API](https://platform.claude.com/docs/en/build-with-claude/vision#files-api-image-example) and referencing by `file_id` to keep request payloads small.

  Even when using the Files API, requests with many large images can fail before reaching the 600-image count. Reduce image dimensions or file sizes (for example, by downsampling) before uploading (see [Resolution and token cost](https://platform.claude.com/docs/en/build-with-claude/vision#evaluate-image-size)).
</Note>

### Supported formats

Claude supports JPEG, PNG, GIF, and WebP images (`image/jpeg`, `image/png`, `image/gif`, `image/webp`). Animations are unsupported, and only the first frame is used.

### Resolution and token cost

Claude views images in patches instead of pixels. Each patch is a 28×28-pixel block of the image, referred to as a visual token. An image, therefore, costs `⌈width / 28⌉ × ⌈height / 28⌉` visual tokens.

Each model has a maximum native image resolution, expressed as a long-edge limit and a visual-token limit. Images larger than either limit are downscaled before processing; see [How Claude resizes and pads images](https://platform.claude.com/docs/en/build-with-claude/vision-coordinates#how-claude-resizes-and-pads-images) for the exact rule. The exception is screenshots and zoom images that you return to the [computer use](https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool#handle-coordinate-scaling-for-higher-resolutions) and [browser use](https://platform.claude.com/docs/en/agents-and-tools/tool-use/browser-use-tool#targets-and-coordinates) toolsets: the API rejects a `tool_result` image that exceeds the model's limits with a validation error instead of downscaling it, so resize those images in your application before returning them. To have any other oversized image rejected with an error instead of downscaled, set the image block's [`transformations` field](https://platform.claude.com/docs/en/build-with-claude/vision-coordinates#oversized-image-error).

| Resolution tier | Models                      | Max long edge | Max visual tokens |
| --------------- | --------------------------- | ------------- | ----------------- |
| High-resolution | Claude 4.7 and later models | 2576 px       | 4784              |
| Standard        | All other models            | 1568 px       | 1568              |

High-resolution support is automatic on the listed models and requires no beta header or client-side opt-in.

The following table shows the downsized resolution and visual-token cost for several image sizes on each tier:

| Image size                     | Standard tier: downsized to | Standard tier: tokens | High-resolution tier: downsized to | High-resolution tier: tokens |
| ------------------------------ | --------------------------- | --------------------- | ---------------------------------- | ---------------------------- |
| 200x200 px (0.04 megapixels)   | Not resized                 | 64                    | Not resized                        | 64                           |
| 1000x1000 px (1 megapixel)     | Not resized                 | 1296                  | Not resized                        | 1296                         |
| 1092x1092 px (1.19 megapixels) | Not resized                 | 1521                  | Not resized                        | 1521                         |
| 1920x1080 px (2.07 megapixels) | 1456x819 px                 | 1560                  | Not resized                        | 2691                         |
| 2000x1500 px (3 megapixels)    | 1269x952 px                 | 1564                  | Not resized                        | 3888                         |
| 3840x2160 px (8.29 megapixels) | 1456x819 px                 | 1560                  | 2576x1449 px                       | 4784                         |

When an image is downsized, Claude scales it to the largest size that fits the tier's limits while preserving its aspect ratio. This caps the token cost. For the precise rule and a reference implementation, see [How Claude resizes and pads images](https://platform.claude.com/docs/en/build-with-claude/vision-coordinates#how-claude-resizes-and-pads-images).

To estimate cost, multiply the token count by the [per-token price of the model](https://claude.com/pricing) you're using. For example, at Claude Haiku 4.5's $1 USD per million input tokens (standard tier), the 1000×1000 image costs about $1.30 USD per thousand images. At Claude Opus 5's $5 USD per million (high-resolution tier), the same image costs about $6.48 USD per thousand and the 4K image about $23.92 USD per thousand.

High-resolution images can use up to roughly three times more visual tokens than the same image on a standard-tier model. If you don't need the additional fidelity that high resolution provides for computer use, screenshot understanding, and dense documents, downsample images before sending to control token costs. To minimize latency and to simplify [coordinate-based workflows](https://platform.claude.com/docs/en/build-with-claude/vision-coordinates), prefer resizing images before uploading them.

### Image quality guidance

When providing images to Claude, keep the following in mind for best results:

* **Image clarity:** Ensure images are clear and not too blurry or pixelated.
* **Text:** If the image contains important text, make sure it's legible and not too small. Avoid cropping out key visual context solely to enlarge the text.
* **Resizing:** Take into account that your image might be resized if it is too large (see [Resolution and token cost](https://platform.claude.com/docs/en/build-with-claude/vision#evaluate-image-size)); this might, for example, make text less legible. Consider pre-resizing your images, cropping them, or both. To have an oversized image rejected with an error instead of resized (important for [coordinate workflows](https://platform.claude.com/docs/en/build-with-claude/vision-coordinates)), mark the image block with [`"oversized_image": "error"`](https://platform.claude.com/docs/en/build-with-claude/vision-coordinates#oversized-image-error).
* **Image compression:** Compressing images before sending them, using a lossy format such as JPEG or WebP (lossy mode), can reduce latency by reducing the size of requests. However, this can introduce artifacts that are detrimental to model performance, especially when multiple compression passes are applied. For example, heavy JPEG compression can make text difficult to read. Confirm your compression settings are appropriate for the task by inspecting the actual images sent to the API.

***


## Coordinates and bounding boxes

Source: https://platform.claude.com/llms-full.txt#coordinates-and-bounding-boxes

For bounding boxes, points, and pixel coordinates, see [Coordinates and bounding boxes](https://platform.claude.com/docs/en/build-with-claude/vision-coordinates). Claude returns absolute pixel coordinates relative to the image it sees after resizing; that guide covers how Claude resizes and pads images and how to pre-resize or rescale so coordinates line up with your original image.

***


## Limitations

Source: https://platform.claude.com/llms-full.txt#limitations-7

Although Claude's image understanding capabilities are cutting-edge, there are some limitations to be aware of:

* **People identification:** Claude [cannot be used](https://www.anthropic.com/legal/aup) to name people in images and refuses to do so.
* **Accuracy:** Claude might hallucinate or make mistakes when interpreting low-quality, rotated, or very small images under 200 pixels.
* **Spatial reasoning:** Claude's coordinate and localization outputs are approximate. Follow the guidance in [Coordinates and bounding boxes](https://platform.claude.com/docs/en/build-with-claude/vision-coordinates) and verify outputs before relying on them.
* **Counting:** Claude can give approximate counts of objects in an image but might not always be precisely accurate, especially with large numbers of small objects.
* **AI-generated images:** Claude cannot determine whether an image is AI-generated and might be incorrect if asked. Do not rely on it to detect fake or synthetic images.
* **Inappropriate content:** Claude does not process inappropriate or explicit images that violate the [Acceptable Use Policy](https://www.anthropic.com/legal/aup).
* **Healthcare applications:** Although Claude can analyze general medical images, it is not designed to interpret complex diagnostic scans such as CTs or MRIs. Claude's outputs should not be considered a substitute for professional medical advice or diagnosis.

Always carefully review and verify Claude's image interpretations, especially for high-stakes use cases. Do not use Claude for tasks requiring perfect precision or sensitive image analysis without human oversight.

***


## FAQ

Source: https://platform.claude.com/llms-full.txt#faq-6

<AccordionGroup>
  <Accordion title="What image file types does Claude support?">
    JPEG, PNG, GIF, and WebP. See [Supported formats](https://platform.claude.com/docs/en/build-with-claude/vision#supported-formats).
  </Accordion>

  <Accordion title="Can Claude read image URLs?">
    Yes. Use the `url` source type instead of `base64` in the `image` content block. See the [URL-based image example](https://platform.claude.com/docs/en/build-with-claude/vision#url-based-image-example).
  </Accordion>

  <Accordion title="Is there a limit to the image file size I can upload?">
    Yes. See [Request limits](https://platform.claude.com/docs/en/build-with-claude/vision#request-limits) for per-image and overall request size limits across the Claude API, Amazon Bedrock, Google Cloud, and claude.ai.
  </Accordion>

  <Accordion title="How many images can I include in one request?">
    Up to 600 per API request (100 for models with a 200k-token context window) and 20 per turn on claude.ai. See [Request limits](https://platform.claude.com/docs/en/build-with-claude/vision#request-limits) for details and the lower per-image dimension limit that applies above 20 images.
  </Accordion>

  <Accordion title="Does Claude read image metadata?">
    No, Claude does not parse or receive any metadata from images passed to it.
  </Accordion>

  <Accordion title="Can I delete images I've uploaded?">
    No. Image uploads are ephemeral and not stored beyond the duration of the API request. Uploaded images are automatically deleted after they have been processed.
  </Accordion>

  <Accordion title="Where can I find details on data privacy for image uploads?">
    Refer to the Anthropic privacy policy page for information on how uploaded images and other data are handled. Anthropic does not use uploaded images to train models.
  </Accordion>

  <Accordion title="What if Claude's image interpretation seems wrong?">
    If Claude's image interpretation seems incorrect:

    1. Ensure the image is clear, high-quality, and correctly oriented.
    2. Try prompt engineering techniques to improve results.
    3. If the issue persists, flag the output in claude.ai (thumbs up/down) or contact the [support team](https://support.claude.com/).

    Your feedback helps improve Claude!
  </Accordion>

  <Accordion title="Can Claude generate or edit images?">
    No, Claude is an image understanding model only. It can interpret and analyze images, but it cannot generate, produce, edit, manipulate, or create images.
  </Accordion>
</AccordionGroup>

***


## Next steps

Source: https://platform.claude.com/llms-full.txt#next-steps-55

<CardGroup cols={2}>
  <Card title="Multimodal cookbook" icon="image" href="https://platform.claude.com/cookbook/multimodal-getting-started-with-vision">
    Get tips and best-practice techniques for tasks such as interpreting charts and extracting content from forms.
  </Card>

  <Card title="API reference" icon="code" href="https://platform.claude.com/docs/en/api/messages/create">
    See the Messages API documentation, including example API calls involving images.
  </Card>
</CardGroup>


### Skills

---
title: Agent Skills
url: https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview
description: Agent Skills are modular capabilities that extend Claude's functionality. Each Skill packages instructions, metadata, and optional resources (scripts, templates) that Claude uses automatically when relevant.
---

<Note>
  To learn how zero data retention (ZDR) applies to this feature, see [API and data retention](https://platform.claude.com/docs/en/manage-claude/api-and-data-retention).
</Note>


## Why use Skills

Source: https://platform.claude.com/llms-full.txt#why-use-skills

Skills are reusable, filesystem-based resources that give Claude domain-specific expertise: workflows, context, and best practices that turn a general-purpose agent into a specialist. Unlike prompts (conversation-level instructions for one-off tasks), Skills load on demand, so you don't have to repeat the same guidance across conversations.

**Key benefits:**

* **Specialize Claude:** Tailor capabilities for domain-specific tasks
* **Reduce repetition:** Create once, use automatically
* **Compose capabilities:** Combine Skills for complex, multistep tasks

<Note>
  For more on the architecture and real-world applications of Agent Skills, see the engineering blog post [Equipping agents for the real world with Agent Skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills).
</Note>


## Using Skills

Source: https://platform.claude.com/llms-full.txt#using-skills

Anthropic provides pre-built Agent Skills for common document tasks (PowerPoint, Excel, Word, PDF), and you can create your own custom Skills. Both work the same way: once a Skill is available in your environment, Claude uses it automatically when relevant to your request.

**Pre-built Agent Skills** are available on claude.ai, the Claude API, [Claude Platform on AWS](https://platform.claude.com/docs/en/build-with-claude/claude-platform-on-aws), and [Microsoft Foundry](https://platform.claude.com/docs/en/build-with-claude/claude-in-microsoft-foundry). On Microsoft Foundry, Agent Skills require a [Hosted on Anthropic deployment](https://platform.claude.com/docs/en/build-with-claude/claude-in-microsoft-foundry#additional-features-not-supported-when-hosted-on-azure). See [Available Skills](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview#available-skills) for the complete list.

**Custom Skills** let you package domain expertise and organizational knowledge. They're available across Claude's products: create them in Claude Code, upload them through the Claude API, or add them in claude.ai settings. On [Claude Platform on AWS](https://platform.claude.com/docs/en/build-with-claude/claude-platform-on-aws) and [Microsoft Foundry](https://platform.claude.com/docs/en/build-with-claude/claude-in-microsoft-foundry), upload custom Skills through the Skills API.

<Note>
  **Get started:**

  * For pre-built Agent Skills: See the [quickstart tutorial](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/quickstart) to start using PowerPoint, Excel, Word, and PDF Skills in the API
  * For custom Skills: See the [Agent Skills Cookbook](https://platform.claude.com/cookbook/skills-notebooks-01-skills-introduction) to learn how to create your own Skills
</Note>


## How Skills work

Source: https://platform.claude.com/llms-full.txt#how-skills-work

Skills use Claude's VM environment to provide capabilities beyond what's possible with prompts alone. Claude operates in a virtual machine with filesystem access, allowing Skills to exist as directories containing instructions, executable code, and reference materials, organized like an onboarding guide you'd create for a new team member.

This filesystem-based architecture enables **progressive disclosure:** Claude loads information in stages as needed, rather than consuming context upfront.

Skills can contain three types of content, each loaded at a different time:

### Level 1: Metadata (always loaded)

The Skill's YAML frontmatter provides discovery information:

Claude loads this metadata at startup and includes it in the system prompt. The `description` is what Claude matches your request against when determining whether to trigger the Skill, so it must say both what the Skill does and when to use it. This lightweight approach means you can install many Skills without context penalty: until a Skill is triggered, only its name and description occupy context.

### Level 2: Instructions (loaded when triggered)

The main body of SKILL.md contains procedural knowledge: workflows, best practices, and guidance:

````markdown
# PDF Processing


## Quick start

Source: https://platform.claude.com/llms-full.txt#quick-start-9

Use pdfplumber to extract text from PDFs:

For advanced form filling, see [FORMS.md](FORMS.md).
````

When you request something that matches a Skill's description, Claude reads SKILL.md from the filesystem using bash. Only then does this content enter the context window.

### Level 3: Resources and code (loaded as needed)

Skills can bundle additional materials:

* `pdf-processing/`

  * `SKILL.md` (main instructions)
  * `FORMS.md` (form-filling guide)
  * `REFERENCE.md` (detailed API reference)
  * `scripts/`
    * `fill_form.py` (utility script)

**Instructions:** Additional markdown files (FORMS.md, REFERENCE.md) containing specialized guidance and workflows

**Code:** Executable scripts (fill\_form.py, validate.py) that Claude runs using bash, providing deterministic operations without loading their code into context

**Resources:** Reference materials such as database schemas, API documentation, templates, or examples

Claude accesses these files only when referenced. The filesystem model means each content type has different strengths: instructions for flexible guidance, code for reliability, resources for factual lookup.

| Level                     | When loaded             | Token cost             | Content                                                                                                                    |
| ------------------------- | ----------------------- | ---------------------- | -------------------------------------------------------------------------------------------------------------------------- |
| **Level 1: Metadata**     | Always (at startup)     | \~100 tokens per Skill | `name` and `description` from YAML frontmatter                                                                             |
| **Level 2: Instructions** | When Skill is triggered | Under 5k tokens        | SKILL.md body with instructions and guidance                                                                               |
| **Level 3+: Resources**   | As needed               | None until accessed    | Bundled files. Reference files load into context when read. Scripts run through bash, and only their output enters context |

Progressive disclosure ensures only relevant content occupies the context window at any given time.

### The Skills architecture

Skills run in a code execution environment where Claude has filesystem access, bash commands, and code execution capabilities. Skills exist as directories on a virtual machine, and Claude interacts with them using the same bash commands you'd use to navigate files on your computer.

![Agent Skills Architecture - showing how Skills integrate with the agent's configuration and virtual machine](https://platform.claude.com/docs/images/agent-skills-architecture.png)

**How Claude accesses Skill content:**

When a Skill is triggered, Claude uses bash to read SKILL.md from the filesystem, bringing its instructions into the context window. If those instructions reference other files (such as FORMS.md or a database schema), Claude reads those files too using additional bash commands. When instructions mention executable scripts, Claude runs them through bash and receives only the output (the script code itself never enters context).

**What this architecture enables:**

* **On-demand file access:** Claude reads only the files each task needs. A Skill can include dozens of reference files, but if your task only needs the sales schema, that's the one file Claude loads. The rest stay on the filesystem and cost zero tokens.
* **Efficient script execution:** When Claude runs `validate_form.py`, the script's code never loads into the context window. Only its output (such as "Validation passed" or a specific error message) consumes tokens, which makes scripts far more efficient than having Claude generate equivalent code on the fly.
* **No practical limit on bundled content:** Files don't consume context until accessed, so Skills can include comprehensive API documentation, large datasets, or extensive examples. There's no context penalty for bundled content that isn't used.

### Example: Loading a PDF processing Skill

Here's how Claude loads and uses the custom `pdf-processing` Skill from the earlier examples (not the pre-built `pdf` Skill):

1. **Startup:** System prompt includes: `pdf-processing - Extract text and tables from PDF files, fill forms, merge documents. Use when working with PDF files or when the user mentions PDFs, forms, or document extraction.`
2. **User request:** "Extract the text from this PDF and summarize it"
3. **Claude invokes:** `bash: cat pdf-processing/SKILL.md` → Instructions loaded into context
4. **Claude determines:** Form filling is not needed, so FORMS.md is not read
5. **Claude executes:** Uses instructions from SKILL.md to complete the task

![Skills loading into context window - showing the progressive loading of skill metadata and content](https://platform.claude.com/docs/images/agent-skills-context-window.png)


## Where Skills work

Source: https://platform.claude.com/llms-full.txt#where-skills-work

Skills are available across Claude's agent products:

<Note>
  Claude Platform on AWS and Microsoft Foundry inherit the same Skills behavior as the Claude API in all following sections.
</Note>

### Claude API

The Claude API supports both pre-built Agent Skills and custom Skills. Both work identically: specify the relevant `skill_id` in the `container` parameter along with the [code execution tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/code-execution-tool).

**Prerequisites:** Using Skills through the API requires the [code execution tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/code-execution-tool), whose container Skills run in.

Use pre-built Agent Skills by referencing their `skill_id` (`pptx`, `xlsx`, `docx`, or `pdf`), or create and upload your own through the Skills API (`/v1/skills` endpoints). Custom Skills are shared workspace-wide: all workspace members can access them.

Skills on the API run in a sandboxed container with no network access and no runtime package installation. See [Limitations and constraints](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview#limitations-and-constraints) for details.

To learn more, see [Using Agent Skills with the API](https://platform.claude.com/docs/en/build-with-claude/skills-guide).

### Claude Code

[Claude Code](https://code.claude.com/docs/en/overview) supports custom Skills. The pre-built document Skills (PowerPoint, Excel, Word, PDF) are not available in Claude Code, though the open-source [Claude API skill](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/claude-api-skill) comes bundled with it. See the full list of [built-in commands and Skills](https://code.claude.com/docs/en/commands) that ship with Claude Code.

**Custom Skills:** Create Skills as directories with SKILL.md files. Claude discovers and uses them automatically.

Custom Skills in Claude Code are filesystem-based and don't require API uploads: place them in `~/.claude/skills/` (personal) or `.claude/skills/` (project).

To learn more, see [Use Skills in Claude Code](https://code.claude.com/docs/en/skills).

### claude.ai

[claude.ai](https://claude.ai) supports both pre-built Agent Skills and custom Skills.

**Pre-built Agent Skills:** These Skills are active when you create documents. Claude uses them with no setup required.

**Custom Skills:** Upload your own Skills as zip files through Settings > Features. Available on Pro, Max, Team, and Enterprise plans with [code execution enabled](https://support.claude.com/en/articles/12111783-create-and-edit-files-with-claude). Custom Skills are individual to each user. They are not shared organization-wide and cannot be centrally managed by admins.

To learn more about using Skills in claude.ai, see the following resources in the Claude Help Center:

* [What are Skills?](https://support.claude.com/en/articles/12512176-what-are-skills)
* [Using Skills in Claude](https://support.claude.com/en/articles/12512180-using-skills-in-claude)
* [How to create custom Skills](https://support.claude.com/en/articles/12512198-creating-custom-skills)
* [Teach Claude your way of working using Skills](https://support.claude.com/en/articles/12580051-teach-claude-your-way-of-working-using-skills)


## Skill structure

Source: https://platform.claude.com/llms-full.txt#skill-structure

Every Skill requires a `SKILL.md` file with YAML frontmatter:

```markdown
---
name: your-skill-name
description: Brief description of what this Skill does and when to use it
---

# Your Skill Name


## Instructions

Source: https://platform.claude.com/llms-full.txt#instructions

[Clear, step-by-step guidance for Claude to follow]


## Examples

Source: https://platform.claude.com/llms-full.txt#examples-2

[Concrete examples of using this Skill]
```

**Required fields:** `name` and `description`

**Field requirements:**

`name`:

* Maximum 64 characters
* Must contain only lowercase letters, numbers, and hyphens
* Cannot contain XML tags
* Cannot contain reserved words: "anthropic", "claude"

`description`:

* Must be non-empty
* Maximum 1024 characters
* Cannot contain XML tags

The `description` must include both what the Skill does and when Claude should use it. For complete authoring guidance, see [Skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices).


## Security considerations

Source: https://platform.claude.com/llms-full.txt#security-considerations-4

Use Skills only from trusted sources: those you created yourself or obtained from Anthropic. Skills give Claude new capabilities through instructions and code, which also means a malicious Skill can direct Claude to invoke tools or execute code in ways that don't match the Skill's stated purpose.

<Warning>
  If you must use a Skill from an untrusted or unknown source, exercise extreme caution and thoroughly audit it before use. Depending on what access Claude has when executing the Skill, malicious Skills could lead to data exfiltration, unauthorized system access, or other security risks.
</Warning>

**Key security considerations:**

* **Audit thoroughly:** Review all files bundled in the Skill: SKILL.md, scripts, images, and other resources. Look for unusual patterns such as unexpected network calls, file access patterns, or operations that don't match the Skill's stated purpose
* **External sources are risky:** Skills that fetch data from external URLs pose particular risk, as fetched content may contain malicious instructions. Even trustworthy Skills can be compromised if their external dependencies change over time
* **Tool misuse:** Malicious Skills can invoke tools (file operations, bash commands, code execution) in harmful ways
* **Data exposure:** Skills with access to sensitive data could be designed to leak information to external systems
* **Treat like installing software:** Be especially careful when integrating Skills into production systems with access to sensitive data or critical operations

For organization-scale governance, vetting, and deployment guidance, see [Skills for enterprise](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/enterprise). Claude Enterprise organizations can also turn on [Skill content scanning](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/enterprise#skill-content-scanning) for custom Skills uploaded in claude.ai and Claude Cowork. Scanning doesn't cover Skills uploaded through the Skills API or the Claude Console.


## Available Skills

Source: https://platform.claude.com/llms-full.txt#available-skills

### Pre-built Agent Skills

The following pre-built Agent Skills are available for immediate use:

* **PowerPoint (pptx):** Create presentations, edit slides, analyze presentation content
* **Excel (xlsx):** Create spreadsheets, analyze data, generate reports with charts
* **Word (docx):** Create documents, edit content, format text
* **PDF (pdf):** Generate formatted PDF documents and reports

These Skills are available on the Claude API, [Claude Platform on AWS](https://platform.claude.com/docs/en/build-with-claude/claude-platform-on-aws), [Microsoft Foundry](https://platform.claude.com/docs/en/build-with-claude/claude-in-microsoft-foundry), and claude.ai. See the [quickstart tutorial](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/quickstart) to start using them in the API.

### Open-source Skills

Anthropic also publishes open-source Skills in the [skills repository](https://github.com/anthropics/skills):

* **[Claude API skill](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/claude-api-skill):** Provides Claude with up-to-date API reference material, SDK documentation, and best practices for eight programming languages. Bundled with Claude Code and also available for installation from the skills repository.

### Custom Skills examples

For complete examples of custom Skills, see the [Skills cookbook](https://platform.claude.com/cookbook/skills-notebooks-01-skills-introduction).


## Data retention

Source: https://platform.claude.com/llms-full.txt#data-retention-9

Agent Skills is not covered by ZDR arrangements. Skill definitions and execution data are retained according to Anthropic's standard data retention policy.

For ZDR eligibility across all features, see [API and data retention](https://platform.claude.com/docs/en/manage-claude/api-and-data-retention).

For audit logging of Skills API operations, see [Audit logging](https://platform.claude.com/docs/en/build-with-claude/skills-guide#audit-logging) in Using Agent Skills with the API.


## Limitations and constraints

Source: https://platform.claude.com/llms-full.txt#limitations-and-constraints

Claude Platform on AWS and Microsoft Foundry follow the same limitations as the Claude API in the following subsections.

### Cross-surface availability

**Custom Skills do not sync across surfaces**. Skills uploaded to one surface are not automatically available on others:

* Skills uploaded to claude.ai must be separately uploaded to the API
* Skills uploaded through the API are not available on claude.ai
* Claude Code Skills are filesystem-based and separate from both claude.ai and API

Manage and upload Skills separately for each surface where you want to use them.

### Sharing scope

Skills have different sharing models depending on where you use them:

* **claude.ai:** Individual user only. Each team member must upload separately.
* **Claude API:** Workspace-wide. All workspace members can access uploaded Skills.
* **Claude Code:** Personal (`~/.claude/skills/`) or project-based (`.claude/skills/`). Can also be shared through Claude Code Plugins.

claude.ai does not support centralized admin management or org-wide distribution of custom Skills.

### Runtime environment constraints

The exact runtime environment available to your Skill depends on the product surface where you use it.

* **claude.ai:**
  * **Varying network access:** Depending on user/admin settings, Skills may have full, partial, or no network access. For more details, see the [Create and Edit Files](https://support.claude.com/en/articles/12111783-create-and-edit-files-with-claude#h_6b7e833898) support article.

* **Claude API:**

  * **No network access:** Skills cannot make external API calls or access the internet.
  * **No runtime package installation:** Only pre-installed packages are available. You cannot install new packages during execution.
  * **Pre-configured dependencies only:** Check the [Code execution tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/code-execution-tool) documentation for the list of available packages.

* **Claude Code:**

  * **Full network access:** Skills have the same network access as any other program on the user's computer.
  * **Global package installation discouraged:** Skills should only install packages locally to avoid interfering with the user's computer.

Plan your Skills to work within these constraints.


## Next steps

Source: https://platform.claude.com/llms-full.txt#next-steps-56

<CardGroup cols={2}>
  <Card title="Get started with Agent Skills in the API" icon="graduation-cap" href="https://platform.claude.com/docs/en/agents-and-tools/agent-skills/quickstart">
    Learn how to use Agent Skills to create documents with the Claude API in under 10 minutes.
  </Card>

  <Card title="Using Agent Skills with the API" icon="code" href="https://platform.claude.com/docs/en/build-with-claude/skills-guide">
    Learn how to use Agent Skills to extend Claude's capabilities through the API.
  </Card>

  <Card title="Use Skills in Claude Code" icon="terminal" href="https://code.claude.com/docs/en/skills">
    Create and manage custom Skills in Claude Code.
  </Card>

  <Card title="Skill authoring best practices" icon="lightbulb" href="https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices">
    Learn how to write effective Skills that Claude can discover and use successfully.
  </Card>
</CardGroup>


---
title: Get started with Agent Skills in the API
url: https://platform.claude.com/docs/en/agents-and-tools/agent-skills/quickstart
description: Learn how to use Agent Skills to create documents with the Claude API in under 10 minutes.
---

This tutorial shows you how to use Agent Skills to create a PowerPoint presentation. You'll learn how to enable Skills, make a request, and access the generated file.


## Prerequisites

Source: https://platform.claude.com/llms-full.txt#prerequisites-3

* A [Claude API key](https://platform.claude.com/settings/keys) or a logged-in [ant CLI](https://platform.claude.com/docs/en/cli-sdks-libraries/cli/authentication)
* A [client SDK](https://platform.claude.com/docs/en/cli-sdks-libraries/overview) for your language, or `curl` and `jq`
* Basic familiarity with making API requests


## Agent Skills overview

Source: https://platform.claude.com/llms-full.txt#agent-skills-overview

Pre-built Agent Skills extend Claude's capabilities with specialized expertise for tasks such as creating documents, analyzing data, and processing files. Anthropic provides the following pre-built Agent Skills in the API:

* **PowerPoint (pptx):** Create and edit presentations
* **Excel (xlsx):** Create and analyze spreadsheets
* **Word (docx):** Create and edit documents
* **PDF (pdf):** Generate PDF documents

<Note>
  To create custom Skills, see the [Agent Skills Cookbook](https://platform.claude.com/cookbook/skills-notebooks-01-skills-introduction) for examples of building your own Skills with domain-specific expertise.
</Note>


## Step 1: List available Skills

Source: https://platform.claude.com/llms-full.txt#step-1-list-available-skills

First, check what Skills are available. Use the Skills API to list all Anthropic-managed Skills. Each language tab is an excerpt from one continuous script, with any imports and client setup at the top:

<CodeGroup defaultLanguage="CLI">
  ```bash cURL
  # List Anthropic-managed Skills
  curl --fail-with-body -sS "https://api.anthropic.com/v1/skills?source=anthropic" \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01"

bash CLI
  # List Anthropic-managed Skills
  ant skills list --source anthropic

python Python
  # List Anthropic-managed Skills
  skills = client.skills.list(source="anthropic")

  for skill in skills.data:
      print(f"{skill.id}: {skill.display_name}")

typescript TypeScript
  // List Anthropic-managed Skills
  const skills = await client.skills.list({ source: "anthropic" });

  for (const skill of skills.data) {
    console.log(`${skill.id}: ${skill.display_name}`);
  }

csharp C#
  // List Anthropic-managed Skills
  var skills = await client.Skills.List(new SkillListParams { Source = "anthropic" });

  foreach (var skill in skills.Items)
  {
      Console.WriteLine($"{skill.ID}: {skill.DisplayName}");
  }

go Go
  // List Anthropic-managed Skills
  skills, err := client.Skills.List(ctx, anthropic.SkillListParams{
  	Source: anthropic.String("anthropic"),
  })
  if err != nil {
  	panic(err)
  }

  for _, skill := range skills.Data {
  	fmt.Printf("%s: %s\n", skill.ID, skill.DisplayName)
  }

java Java
  // List Anthropic-managed Skills
  SkillListPage skills = client.skills().list(
      SkillListParams.builder().source("anthropic").build()
  );

  for (Skill skill : skills.data()) {
      IO.println(skill.id() + ": " + skill.displayName());
  }

php PHP
  // List Anthropic-managed Skills
  $skills = $client->skills->list(source: 'anthropic');

  foreach ($skills->getItems() as $skill) {
      echo "{$skill->id}: {$skill->displayName}\n";
  }

ruby Ruby
  # List Anthropic-managed Skills
  skills = client.skills.list(source: "anthropic")

  skills.data.each do |skill|
    puts "#{skill.id}: #{skill.display_name}"
  end
  ```
</CodeGroup>

You see the following Skills: `pptx`, `xlsx`, `docx`, and `pdf`.

This API returns each Skill's metadata: its name and description. Claude loads this metadata at startup to determine which Skills are available. This is the first level of **progressive disclosure**, where Claude discovers Skills without loading their full instructions yet.


## Step 2: Create a presentation

Source: https://platform.claude.com/llms-full.txt#step-2-create-a-presentation

Use the PowerPoint Skill to create a presentation about renewable energy. Specify Skills using the `container` parameter in the Messages API:

<CodeGroup>
  ```bash cURL
  # Create a message with the PowerPoint Skill
  response=$(
    curl --fail-with-body -sS https://api.anthropic.com/v1/messages \
      -H "content-type: application/json" \
      -H "x-api-key: $ANTHROPIC_API_KEY" \
      -H "anthropic-version: 2023-06-01" \
      -d @- <<'EOF'
  {
    "model": "claude-opus-5",
    "max_tokens": 16000,
    "container": {
      "skills": [{"type": "anthropic", "skill_id": "pptx", "version": "latest"}]
    },
    "messages": [
      {"role": "user", "content": "Create a presentation about renewable energy with 5 slides"}
    ],
    "tools": [{"type": "code_execution_20260521", "name": "code_execution"}]
  }
  EOF
  )

bash CLI
  # Create a message with the PowerPoint Skill
  response=$(ant messages create --format json <<'YAML'
  model: claude-opus-5
  max_tokens: 16000
  container:
    skills:
      - type: anthropic
        skill_id: pptx
        version: latest
  messages:
    - role: user
      content: Create a presentation about renewable energy with 5 slides
  tools:
    - type: code_execution_20260521
      name: code_execution
  YAML
  )

python Python
  # Create a message with the PowerPoint Skill
  response = client.messages.create(
      model="claude-opus-5",
      max_tokens=16000,
      container={
          "skills": [{"type": "anthropic", "skill_id": "pptx", "version": "latest"}]
      },
      messages=[
          {
              "role": "user",
              "content": "Create a presentation about renewable energy with 5 slides",
          }
      ],
      tools=[{"type": "code_execution_20260521", "name": "code_execution"}],
  )

  print(f"stop_reason={response.stop_reason}, blocks={len(response.content)}")

typescript TypeScript
  // Create a message with the PowerPoint Skill
  const response = await client.messages.create({
    model: "claude-opus-5",
    max_tokens: 16000,
    container: {
      skills: [{ type: "anthropic", skill_id: "pptx", version: "latest" }],
    },
    messages: [
      {
        role: "user",
        content: "Create a presentation about renewable energy with 5 slides",
      },
    ],
    tools: [{ type: "code_execution_20260521", name: "code_execution" }],
  });

  console.log(
    `stop_reason=${response.stop_reason}, blocks=${response.content.length}`,
  );

csharp C#
  // Create a message with the PowerPoint Skill
  var response = await client.Messages.Create(new MessageCreateParams
  {
      Model = Model.ClaudeOpus5,
      MaxTokens = 16000,
      Container = new ContainerParams
      {
          Skills =
          [
              new SkillParams
              {
                  Type = SkillParamsType.Anthropic,
                  SkillID = "pptx",
                  Version = "latest",
              },
          ],
      },
      Messages =
      [
          new MessageParam
          {
              Role = Role.User,
              Content = "Create a presentation about renewable energy with 5 slides",
          },
      ],
      Tools = [new CodeExecutionTool20260521()],
  });

  Console.WriteLine($"stop_reason={response.StopReason?.Raw()}, blocks={response.Content.Count}");

go Go
  // Create a message with the PowerPoint Skill
  response, err := client.Messages.New(ctx, anthropic.MessageNewParams{
  	Model:     anthropic.ModelClaudeOpus5,
  	MaxTokens: 16000,
  	Container: anthropic.MessageCreateParamsContainerUnion{
  		OfContainers: &anthropic.ContainerParams{
  			Skills: []anthropic.SkillParams{
  				{
  					Type:    anthropic.SkillParamsTypeAnthropic,
  					SkillID: "pptx",
  					Version: anthropic.String("latest"),
  				},
  			},
  		},
  	},
  	Messages: []anthropic.MessageParam{
  		anthropic.NewUserMessage(
  			anthropic.NewTextBlock("Create a presentation about renewable energy with 5 slides"),
  		),
  	},
  	Tools: []anthropic.ToolUnionParam{
  		{OfCodeExecutionTool20260521: &anthropic.CodeExecutionTool20260521Param{}},
  	},
  })
  if err != nil {
  	panic(err)
  }

  fmt.Printf("stop_reason=%s, blocks=%d\n", response.StopReason, len(response.Content))

java Java
  // Create a message with the PowerPoint Skill
  Message response = client.messages().create(
      MessageCreateParams.builder()
          .model(Model.CLAUDE_OPUS_5)
          .maxTokens(16000)
          .container(
              ContainerParams.builder()
                  .addSkill(
                      SkillParams.builder()
                          .type(SkillParams.Type.ANTHROPIC)
                          .skillId("pptx")
                          .version("latest")
                          .build()
                  )
                  .build()
          )
          .addUserMessage("Create a presentation about renewable energy with 5 slides")
          .addTool(CodeExecutionTool20260521.builder().build())
          .build()
  );

  IO.println(
      "stop_reason=" + response.stopReason().orElse(null)
          + ", blocks=" + response.content().size()
  );

php PHP
  // Create a message with the PowerPoint Skill
  $response = $client->messages->create(
      model: 'claude-opus-5',
      maxTokens: 16000,
      container: [
          'skills' => [['type' => 'anthropic', 'skillID' => 'pptx', 'version' => 'latest']],
      ],
      messages: [
          [
              'role' => 'user',
              'content' => 'Create a presentation about renewable energy with 5 slides',
          ],
      ],
      tools: [['type' => 'code_execution_20260521', 'name' => 'code_execution']],
  );

  printf("stop_reason=%s, blocks=%d\n", $response->stopReason, count($response->content));

ruby Ruby
  # Create a message with the PowerPoint Skill
  response = client.messages.create(
    model: "claude-opus-5",
    max_tokens: 16_000,
    container: {
      skills: [{type: "anthropic", skill_id: "pptx", version: "latest"}]
    },
    messages: [
      {
        role: "user",
        content: "Create a presentation about renewable energy with 5 slides"
      }
    ],
    tools: [{type: "code_execution_20260521", name: "code_execution"}]
  )

  puts "stop_reason=#{response.stop_reason}, blocks=#{response.content.length}"
  ```
</CodeGroup>

The request includes the following parts:

* **`model`:** A [model that supports the code execution tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/code-execution-tool#compatibility)
* **`container.skills`:** Specifies which Skills Claude can use
* **`type: "anthropic"`:** Indicates this is an Anthropic-managed Skill
* **`skill_id: "pptx"`:** The PowerPoint Skill identifier
* **`version: "latest"`:** The Skill version set to the most recently published
* **`tools`:** Enables code execution (required for Skills)

<Note>
  The examples use the `code_execution_20260521` tool version, and the Step 3 code parses the result types that current tool versions return. Skills also work with older [code execution tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/code-execution-tool) versions such as `code_execution_20250825`: any current code execution tool version satisfies the Skills requirement. If you use a different version, use the tool `type` listed on the code execution tool page.
</Note>

When you make this request, Claude automatically matches your task to the relevant Skill. Because you asked for a presentation, Claude determines the PowerPoint Skill is relevant and loads its full instructions: the second level of progressive disclosure. Then Claude runs the Skill's code to create your presentation.


## Step 3: Download the created file

Source: https://platform.claude.com/llms-full.txt#step-3-download-the-created-file

The presentation was created in the code execution container and saved as a file. The Step 2 `response` includes a file reference with a file ID. Extract the file ID and download the file with the Files API. The example saves it to your system temp directory:

<CodeGroup>
  ```bash cURL
  # Extract the file ID. The code execution tool runs the Skill's code through
  # its Bash sub-tool, and generated files appear as bash_code_execution_output
  # items inside the bash_code_execution_tool_result block.
  file_id=$(jq -r '
    last(
      .content[]
      | select(.type == "bash_code_execution_tool_result")
      | .content
      | select(.type == "bash_code_execution_result")
      | .content[].file_id
    ) // empty
  ' <<<"$response")

  if [[ -n "$file_id" ]]; then
    # Download the file and save it
    output_path="${TMPDIR:-/tmp}/renewable_energy.pptx"
    curl --fail-with-body -sS "https://api.anthropic.com/v1/files/$file_id/content" \
      -H "x-api-key: $ANTHROPIC_API_KEY" \
      -H "anthropic-version: 2023-06-01" \
      -o "$output_path"
    echo "Presentation saved to $output_path"
  fi

bash CLI
  # Extract the file ID. The code execution tool runs the Skill's code through
  # its Bash sub-tool, and generated files appear as bash_code_execution_output
  # items inside the bash_code_execution_tool_result block.
  file_id=$(jq -r '
    last(
      .content[]
      | select(.type == "bash_code_execution_tool_result")
      | .content
      | select(.type == "bash_code_execution_result")
      | .content[].file_id
    ) // empty
  ' <<<"$response")

  if [[ -n "$file_id" ]]; then
    # Download the file and save it
    output_path="${TMPDIR:-/tmp}/renewable_energy.pptx"
    ant files download --file-id "$file_id" --output "$output_path"
    echo "Presentation saved to $output_path"
  fi

python Python
  # Extract the file ID. The code execution tool runs the Skill's code through
  # its Bash sub-tool, and generated files appear as bash_code_execution_output
  # items inside the bash_code_execution_tool_result block.
  file_id = None
  for block in response.content:
      if block.type == "bash_code_execution_tool_result":
          if block.content.type == "bash_code_execution_result":
              for output in block.content.content:
                  file_id = output.file_id

  if file_id:
      # Download the file and save it
      output_path = Path(tempfile.gettempdir()) / "renewable_energy.pptx"
      file_content = client.files.download(file_id=file_id)
      file_content.write_to_file(output_path)
      print(f"Presentation saved to {output_path}")

typescript TypeScript
  // Extract the file ID. The code execution tool runs the Skill's code through
  // its Bash sub-tool, and generated files appear as bash_code_execution_output
  // items inside the bash_code_execution_tool_result block.
  let fileId: string | undefined;
  for (const block of response.content) {
    if (
      block.type === "bash_code_execution_tool_result" &&
      block.content.type === "bash_code_execution_result"
    ) {
      for (const output of block.content.content) {
        fileId = output.file_id;
      }
    }
  }

  if (fileId) {
    // Download the file and save it
    const outputPath = path.join(os.tmpdir(), "renewable_energy.pptx");
    const fileContent = await client.files.download(fileId);
    await fs.writeFile(outputPath, Buffer.from(await fileContent.arrayBuffer()));
    console.log(`Presentation saved to ${outputPath}`);
  }

csharp C#
  // Extract the file ID. The code execution tool runs the Skill's code through
  // its Bash sub-tool, and generated files appear as bash_code_execution_output
  // items inside the bash_code_execution_tool_result block.
  string? fileId = null;
  foreach (var block in response.Content)
  {
      if (block.TryPickBashCodeExecutionToolResult(out var bashResult)
          && bashResult.Content.TryPickBashCodeExecutionResultBlock(out var bashResultBlock))
      {
          foreach (var output in bashResultBlock.Content)
          {
              fileId = output.FileID;
          }
      }
  }

  if (fileId is not null)
  {
      // Download the file and save it
      var outputPath = Path.Combine(Path.GetTempPath(), "renewable_energy.pptx");
      using var download = await client.Files.Download(fileId);
      await using var source = await download.ReadAsStream();
      await using var destination = File.Create(outputPath);
      await source.CopyToAsync(destination);
      Console.WriteLine($"Presentation saved to {outputPath}");
  }

go Go
  // Extract the file ID. The code execution tool runs the Skill's code through
  // its Bash sub-tool, and generated files appear as bash_code_execution_output
  // items inside the bash_code_execution_tool_result block.
  var fileID string
  for _, block := range response.Content {
  	switch result := block.AsAny().(type) {
  	case anthropic.BashCodeExecutionToolResultBlock:
  		if result.Content.Type == "bash_code_execution_result" {
  			for _, output := range result.Content.Content {
  				fileID = output.FileID
  			}
  		}
  	}
  }

  if fileID != "" {
  	// Download the file and save it
  	outputPath := filepath.Join(os.TempDir(), "renewable_energy.pptx")
  	fileContent, err := client.Files.Download(ctx, fileID)
  	if err != nil {
  		panic(err)
  	}
  	defer fileContent.Body.Close()
  	outFile, err := os.Create(outputPath)
  	if err != nil {
  		panic(err)
  	}
  	defer outFile.Close()
  	if _, err := io.Copy(outFile, fileContent.Body); err != nil {
  		panic(err)
  	}
  	fmt.Printf("Presentation saved to %s\n", outputPath)
  }

java Java
  // Extract the file ID. The code execution tool runs the Skill's code through
  // its Bash sub-tool, and generated files appear as bash_code_execution_output
  // items inside the bash_code_execution_tool_result block.
  String fileId = null;
  for (ContentBlock block : response.content()) {
      if (block.isBashCodeExecutionToolResult()) {
          var content = block.asBashCodeExecutionToolResult().content();
          if (content.isBashCodeExecutionResultBlock()) {
              for (var output : content.asBashCodeExecutionResultBlock().content()) {
                  fileId = output.fileId();
              }
          }
      }
  }

  if (fileId != null) {
      // Download the file and save it
      Path outputPath = Files.createTempFile("renewable_energy", ".pptx");
      try (HttpResponse fileContent = client.files().download(fileId)) {
          Files.copy(fileContent.body(), outputPath, StandardCopyOption.REPLACE_EXISTING);
      }
      IO.println("Presentation saved to " + outputPath);
  }

php PHP
  // Extract the file ID. The code execution tool runs the Skill's code through
  // its Bash sub-tool, and generated files appear as bash_code_execution_output
  // items inside the bash_code_execution_tool_result block.
  $fileId = null;
  foreach ($response->content as $block) {
      if ($block->type !== 'bash_code_execution_tool_result') {
          continue;
      }
      $resultBlock = $block->content;
      if ($resultBlock->type !== 'bash_code_execution_result') {
          continue;
      }
      foreach ($resultBlock->content as $output) {
          $fileId = $output->fileID;
      }
  }

  if ($fileId !== null) {
      // Download the file and save it
      $outputPath = sys_get_temp_dir() . '/renewable_energy.pptx';
      $fileContent = $client->files->download($fileId);
      file_put_contents($outputPath, $fileContent);
      echo "Presentation saved to {$outputPath}\n";
  }

ruby Ruby
  # Extract the file ID. The code execution tool runs the Skill's code through
  # its Bash sub-tool, and generated files appear as bash_code_execution_output
  # items inside the bash_code_execution_tool_result block.
  file_id = nil
  response.content.each do |block|
    next unless block.type == :bash_code_execution_tool_result

    if block.content[:type].to_s == "bash_code_execution_result"
      Array(block.content[:content]).each { |output| file_id = output[:file_id] }
    end
  end

  if file_id
    # Download the file and save it
    output_path = File.join(Dir.tmpdir, "renewable_energy.pptx")
    file_content = client.files.download(file_id)
    File.binwrite(output_path, file_content.read)
    puts "Presentation saved to #{output_path}"
  end
  ```
</CodeGroup>

<Note>
  For complete details on working with generated files, see [Retrieve generated files](https://platform.claude.com/docs/en/agents-and-tools/tool-use/code-execution-tool#retrieve-generated-files) in the code execution tool documentation.
</Note>


## Try more examples

Source: https://platform.claude.com/llms-full.txt#try-more-examples

Try these variations:

### Create a spreadsheet

<CodeGroup>
  ```bash cURL
  curl --fail-with-body -sS https://api.anthropic.com/v1/messages \
    -H "content-type: application/json" \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -d '{
      "model": "claude-opus-5",
      "max_tokens": 16000,
      "container": {
        "skills": [{"type": "anthropic", "skill_id": "xlsx", "version": "latest"}]
      },
      "messages": [
        {"role": "user", "content": "Create a quarterly sales tracking spreadsheet with sample data"}
      ],
      "tools": [{"type": "code_execution_20260521", "name": "code_execution"}]
    }'

bash CLI
  ant messages create <<'YAML'
  model: claude-opus-5
  max_tokens: 16000
  container:
    skills:
      - type: anthropic
        skill_id: xlsx
        version: latest
  messages:
    - role: user
      content: Create a quarterly sales tracking spreadsheet with sample data
  tools:
    - type: code_execution_20260521
      name: code_execution
  YAML

python Python
  response = client.messages.create(
      model="claude-opus-5",
      max_tokens=16000,
      container={
          "skills": [{"type": "anthropic", "skill_id": "xlsx", "version": "latest"}]
      },
      messages=[
          {
              "role": "user",
              "content": "Create a quarterly sales tracking spreadsheet with sample data",
          }
      ],
      tools=[{"type": "code_execution_20260521", "name": "code_execution"}],
  )

typescript TypeScript
  const response = await client.messages.create({
    model: "claude-opus-5",
    max_tokens: 16000,
    container: {
      skills: [{ type: "anthropic", skill_id: "xlsx", version: "latest" }]
    },
    messages: [
      {
        role: "user",
        content: "Create a quarterly sales tracking spreadsheet with sample data"
      }
    ],
    tools: [{ type: "code_execution_20260521", name: "code_execution" }]
  });

csharp C#
  var response = await client.Messages.Create(
      new MessageCreateParams
      {
          Model = Model.ClaudeOpus5,
          MaxTokens = 16000,
          Container = new ContainerParams
          {
              Skills =
              [
                  new SkillParams
                  {
                      Type = SkillParamsType.Anthropic,
                      SkillID = "xlsx",
                      Version = "latest",
                  },
              ],
          },
          Messages =
          [
              new MessageParam
              {
                  Role = Role.User,
                  Content = "Create a quarterly sales tracking spreadsheet with sample data",
              },
          ],
          Tools = [new CodeExecutionTool20260521()],
      }
  );

go Go
  response, err := client.Messages.New(context.Background(), anthropic.MessageNewParams{
  	Model:     anthropic.ModelClaudeOpus5,
  	MaxTokens: 16000,
  	Container: anthropic.MessageCreateParamsContainerUnion{
  		OfContainers: &anthropic.ContainerParams{
  			Skills: []anthropic.SkillParams{
  				{
  					Type:    anthropic.SkillParamsTypeAnthropic,
  					SkillID: "xlsx",
  					Version: anthropic.String("latest"),
  				},
  			},
  		},
  	},
  	Messages: []anthropic.MessageParam{
  		anthropic.NewUserMessage(anthropic.NewTextBlock("Create a quarterly sales tracking spreadsheet with sample data")),
  	},
  	Tools: []anthropic.ToolUnionParam{
  		{
  			OfCodeExecutionTool20260521: &anthropic.CodeExecutionTool20260521Param{},
  		},
  	},
  })
  if err != nil {
  	panic(err)
  }

java Java
  Message response = client.messages().create(
      MessageCreateParams.builder()
          .model(CLAUDE_OPUS_5)
          .maxTokens(16000)
          .container(
              ContainerParams.builder()
                  .addSkill(
                      SkillParams.builder()
                          .type(ANTHROPIC)
                          .skillId("xlsx")
                          .version("latest")
                          .build()
                  )
                  .build()
          )
          .addUserMessage("Create a quarterly sales tracking spreadsheet with sample data")
          .addTool(CodeExecutionTool20260521.builder().build())
          .build()
  );

php PHP
  $response = $client->messages->create(
      model: 'claude-opus-5',
      maxTokens: 16000,
      container: [
          'skills' => [
              ['type' => 'anthropic', 'skillID' => 'xlsx', 'version' => 'latest'],
          ],
      ],
      messages: [
          [
              'role' => 'user',
              'content' => 'Create a quarterly sales tracking spreadsheet with sample data',
          ],
      ],
      tools: [['type' => 'code_execution_20260521', 'name' => 'code_execution']],
  );

ruby Ruby
  response = client.messages.create(
    model: "claude-opus-5",
    max_tokens: 16_000,
    container: {
      skills: [{type: "anthropic", skill_id: "xlsx", version: "latest"}]
    },
    messages: [
      {
        role: "user",
        content: "Create a quarterly sales tracking spreadsheet with sample data"
      }
    ],
    tools: [{type: "code_execution_20260521", name: "code_execution"}]
  )

bash cURL
  curl --fail-with-body -sS https://api.anthropic.com/v1/messages \
    -H "content-type: application/json" \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -d '{
      "model": "claude-opus-5",
      "max_tokens": 16000,
      "container": {
        "skills": [{"type": "anthropic", "skill_id": "docx", "version": "latest"}]
      },
      "messages": [
        {"role": "user", "content": "Write a 2-page report on the benefits of renewable energy"}
      ],
      "tools": [{"type": "code_execution_20260521", "name": "code_execution"}]
    }'

bash CLI
  ant messages create <<'YAML'
  model: claude-opus-5
  max_tokens: 16000
  container:
    skills:
      - type: anthropic
        skill_id: docx
        version: latest
  messages:
    - role: user
      content: Write a 2-page report on the benefits of renewable energy
  tools:
    - type: code_execution_20260521
      name: code_execution
  YAML

python Python
  response = client.messages.create(
      model="claude-opus-5",
      max_tokens=16000,
      container={
          "skills": [{"type": "anthropic", "skill_id": "docx", "version": "latest"}]
      },
      messages=[
          {
              "role": "user",
              "content": "Write a 2-page report on the benefits of renewable energy",
          }
      ],
      tools=[{"type": "code_execution_20260521", "name": "code_execution"}],
  )

typescript TypeScript
  const response = await client.messages.create({
    model: "claude-opus-5",
    max_tokens: 16000,
    container: {
      skills: [{ type: "anthropic", skill_id: "docx", version: "latest" }]
    },
    messages: [
      {
        role: "user",
        content: "Write a 2-page report on the benefits of renewable energy"
      }
    ],
    tools: [{ type: "code_execution_20260521", name: "code_execution" }]
  });

csharp C#
  var response = await client.Messages.Create(
      new MessageCreateParams
      {
          Model = Model.ClaudeOpus5,
          MaxTokens = 16000,
          Container = new ContainerParams
          {
              Skills =
              [
                  new SkillParams
                  {
                      Type = SkillParamsType.Anthropic,
                      SkillID = "docx",
                      Version = "latest",
                  },
              ],
          },
          Messages =
          [
              new MessageParam
              {
                  Role = Role.User,
                  Content = "Write a 2-page report on the benefits of renewable energy",
              },
          ],
          Tools = [new CodeExecutionTool20260521()],
      }
  );

go Go
  response, err := client.Messages.New(context.Background(), anthropic.MessageNewParams{
  	Model:     anthropic.ModelClaudeOpus5,
  	MaxTokens: 16000,
  	Container: anthropic.MessageCreateParamsContainerUnion{
  		OfContainers: &anthropic.ContainerParams{
  			Skills: []anthropic.SkillParams{
  				{
  					Type:    anthropic.SkillParamsTypeAnthropic,
  					SkillID: "docx",
  					Version: anthropic.String("latest"),
  				},
  			},
  		},
  	},
  	Messages: []anthropic.MessageParam{
  		anthropic.NewUserMessage(anthropic.NewTextBlock("Write a 2-page report on the benefits of renewable energy")),
  	},
  	Tools: []anthropic.ToolUnionParam{
  		{
  			OfCodeExecutionTool20260521: &anthropic.CodeExecutionTool20260521Param{},
  		},
  	},
  })
  if err != nil {
  	panic(err)
  }

java Java
  Message response = client.messages().create(
      MessageCreateParams.builder()
          .model(CLAUDE_OPUS_5)
          .maxTokens(16000)
          .container(
              ContainerParams.builder()
                  .addSkill(
                      SkillParams.builder()
                          .type(ANTHROPIC)
                          .skillId("docx")
                          .version("latest")
                          .build()
                  )
                  .build()
          )
          .addUserMessage("Write a 2-page report on the benefits of renewable energy")
          .addTool(CodeExecutionTool20260521.builder().build())
          .build()
  );

php PHP
  $response = $client->messages->create(
      model: 'claude-opus-5',
      maxTokens: 16000,
      container: [
          'skills' => [
              ['type' => 'anthropic', 'skillID' => 'docx', 'version' => 'latest'],
          ],
      ],
      messages: [
          [
              'role' => 'user',
              'content' => 'Write a 2-page report on the benefits of renewable energy',
          ],
      ],
      tools: [['type' => 'code_execution_20260521', 'name' => 'code_execution']],
  );

ruby Ruby
  response = client.messages.create(
    model: "claude-opus-5",
    max_tokens: 16_000,
    container: {
      skills: [{type: "anthropic", skill_id: "docx", version: "latest"}]
    },
    messages: [
      {
        role: "user",
        content: "Write a 2-page report on the benefits of renewable energy"
      }
    ],
    tools: [{type: "code_execution_20260521", name: "code_execution"}]
  )

bash cURL
  curl --fail-with-body -sS https://api.anthropic.com/v1/messages \
    -H "content-type: application/json" \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -d '{
      "model": "claude-opus-5",
      "max_tokens": 16000,
      "container": {
        "skills": [{"type": "anthropic", "skill_id": "pdf", "version": "latest"}]
      },
      "messages": [
        {"role": "user", "content": "Generate a PDF invoice template"}
      ],
      "tools": [{"type": "code_execution_20260521", "name": "code_execution"}]
    }'

bash CLI
  ant messages create <<'YAML'
  model: claude-opus-5
  max_tokens: 16000
  container:
    skills:
      - type: anthropic
        skill_id: pdf
        version: latest
  messages:
    - role: user
      content: Generate a PDF invoice template
  tools:
    - type: code_execution_20260521
      name: code_execution
  YAML

python Python
  response = client.messages.create(
      model="claude-opus-5",
      max_tokens=16000,
      container={
          "skills": [{"type": "anthropic", "skill_id": "pdf", "version": "latest"}]
      },
      messages=[
          {
              "role": "user",
              "content": "Generate a PDF invoice template",
          }
      ],
      tools=[{"type": "code_execution_20260521", "name": "code_execution"}],
  )

typescript TypeScript
  const response = await client.messages.create({
    model: "claude-opus-5",
    max_tokens: 16000,
    container: {
      skills: [{ type: "anthropic", skill_id: "pdf", version: "latest" }]
    },
    messages: [
      {
        role: "user",
        content: "Generate a PDF invoice template"
      }
    ],
    tools: [{ type: "code_execution_20260521", name: "code_execution" }]
  });

csharp C#
  var response = await client.Messages.Create(
      new MessageCreateParams
      {
          Model = Model.ClaudeOpus5,
          MaxTokens = 16000,
          Container = new ContainerParams
          {
              Skills =
              [
                  new SkillParams
                  {
                      Type = SkillParamsType.Anthropic,
                      SkillID = "pdf",
                      Version = "latest",
                  },
              ],
          },
          Messages =
          [
              new MessageParam
              {
                  Role = Role.User,
                  Content = "Generate a PDF invoice template",
              },
          ],
          Tools = [new CodeExecutionTool20260521()],
      }
  );

go Go
  response, err := client.Messages.New(context.Background(), anthropic.MessageNewParams{
  	Model:     anthropic.ModelClaudeOpus5,
  	MaxTokens: 16000,
  	Container: anthropic.MessageCreateParamsContainerUnion{
  		OfContainers: &anthropic.ContainerParams{
  			Skills: []anthropic.SkillParams{
  				{
  					Type:    anthropic.SkillParamsTypeAnthropic,
  					SkillID: "pdf",
  					Version: anthropic.String("latest"),
  				},
  			},
  		},
  	},
  	Messages: []anthropic.MessageParam{
  		anthropic.NewUserMessage(anthropic.NewTextBlock("Generate a PDF invoice template")),
  	},
  	Tools: []anthropic.ToolUnionParam{
  		{
  			OfCodeExecutionTool20260521: &anthropic.CodeExecutionTool20260521Param{},
  		},
  	},
  })
  if err != nil {
  	panic(err)
  }

java Java
  Message response = client.messages().create(
      MessageCreateParams.builder()
          .model(CLAUDE_OPUS_5)
          .maxTokens(16000)
          .container(
              ContainerParams.builder()
                  .addSkill(
                      SkillParams.builder()
                          .type(ANTHROPIC)
                          .skillId("pdf")
                          .version("latest")
                          .build()
                  )
                  .build()
          )
          .addUserMessage("Generate a PDF invoice template")
          .addTool(CodeExecutionTool20260521.builder().build())
          .build()
  );

php PHP
  $response = $client->messages->create(
      model: 'claude-opus-5',
      maxTokens: 16000,
      container: [
          'skills' => [
              ['type' => 'anthropic', 'skillID' => 'pdf', 'version' => 'latest'],
          ],
      ],
      messages: [
          [
              'role' => 'user',
              'content' => 'Generate a PDF invoice template',
          ],
      ],
      tools: [['type' => 'code_execution_20260521', 'name' => 'code_execution']],
  );

ruby Ruby
  response = client.messages.create(
    model: "claude-opus-5",
    max_tokens: 16_000,
    container: {
      skills: [{type: "anthropic", skill_id: "pdf", version: "latest"}]
    },
    messages: [
      {
        role: "user",
        content: "Generate a PDF invoice template"
      }
    ],
    tools: [{type: "code_execution_20260521", name: "code_execution"}]
  )
  ```
</CodeGroup>


## Next steps

Source: https://platform.claude.com/llms-full.txt#next-steps-57

<CardGroup cols={2}>
  <Card title="Skill authoring best practices" icon="edit" href="https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices">
    Learn how to write effective Skills that Claude can discover and use successfully.
  </Card>

  <Card title="Using Agent Skills with the API" icon="book" href="https://platform.claude.com/docs/en/build-with-claude/skills-guide">
    Learn how to use Agent Skills to extend Claude's capabilities through the API.
  </Card>

  <Card title="Create custom Skills" icon="code" href="https://platform.claude.com/docs/en/api/skills/create">
    Upload your own Skills for specialized tasks.
  </Card>

  <Card title="Use Skills in Claude Code" icon="terminal" href="https://code.claude.com/docs/en/skills">
    Learn about Skills in Claude Code.
  </Card>

  <Card title="Agent Skills Cookbook" icon="book" href="https://platform.claude.com/cookbook/skills-notebooks-01-skills-introduction">
    Explore example Skills and implementation patterns.
  </Card>
</CardGroup>


---
title: Skill authoring best practices
url: https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices
description: Learn how to write effective Skills that Claude can discover and use successfully.
---

Good Skills are concise, well-structured, and tested with real usage. This guide provides practical authoring decisions to help you write Skills that Claude can discover and use effectively.

For conceptual background on how Skills work, see the [Skills overview](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview).


## Core principles

Source: https://platform.claude.com/llms-full.txt#core-principles

### Concise is key

The [context window](https://platform.claude.com/docs/en/build-with-claude/context-windows) is a public good. Your Skill shares the context window with everything else Claude needs to know, including:

* The system prompt
* Conversation history
* Other Skills' metadata
* Your actual request

Not every token in your Skill has an immediate cost. At startup, only the metadata (name and description) from all Skills is pre-loaded. Claude reads SKILL.md only when the Skill becomes relevant, and reads additional files only as needed. However, being concise in SKILL.md still matters: once Claude loads it, every token competes with conversation history and other context.

**Default assumption:** Claude is already very smart

Only add context Claude doesn't already have. Challenge each piece of information:

* "Does Claude really need this explanation?"
* "Can I assume Claude knows this?"
* "Does this paragraph justify its token cost?"

**Good example: Concise** (approximately 50 tokens):

````markdown


## Extract PDF text

Source: https://platform.claude.com/llms-full.txt#extract-pdf-text

Use pdfplumber for text extraction:

`

markdown


## Extract PDF text

Source: https://platform.claude.com/llms-full.txt#extract-pdf-text-2

PDF (Portable Document Format) files are a common file format that contains
text, images, and other content. To extract text from a PDF, you'll need to
use a library. There are many libraries available for PDF processing, but
pdfplumber is recommended because it's easy to use and handles most cases well.
First, you'll need to install it using pip. Then you can use the code below...

markdown


## Code review process

Source: https://platform.claude.com/llms-full.txt#code-review-process

1. Analyze the code structure and organization
2. Check for potential bugs or edge cases
3. Suggest improvements for readability and maintainability
4. Verify adherence to project conventions

`markdown


## Generate report

Source: https://platform.claude.com/llms-full.txt#generate-report

Use this template and customize as needed:

`

`markdown


## Database migration

Source: https://platform.claude.com/llms-full.txt#database-migration

Run exactly this script:

Do not modify the command or add additional flags.
````

**Analogy:** Think of Claude as a robot exploring a path:

* **Narrow bridge with cliffs on both sides:** There's only one safe way forward. Provide specific guardrails and exact instructions (low freedom). Example: database migrations that must run in exact sequence.
* **Open field with no hazards:** Many paths lead to success. Give general direction and trust Claude to find the best route (high freedom). Example: code reviews where context determines the best approach.

### Test with all models you plan to use

Skills act as additions to models, so effectiveness depends on the underlying model. Test your Skill with all the models you plan to use it with.

**Testing considerations by model:**

* **Claude Haiku** (fast, economical): Does the Skill provide enough guidance?
* **Claude Sonnet** (balanced): Is the Skill clear and efficient?
* **Claude Opus** (powerful reasoning): Does the Skill avoid over-explaining?

What works perfectly for Opus might need more detail for Haiku. If you plan to use your Skill across multiple models, aim for instructions that work well with all of them.


## Skill structure

Source: https://platform.claude.com/llms-full.txt#skill-structure-2

<Note>
  **YAML Frontmatter:** The SKILL.md frontmatter requires two fields:

  `name`:

  * Maximum 64 characters
  * Must contain only lowercase letters, numbers, and hyphens
  * Cannot contain XML tags
  * Cannot contain reserved words: "anthropic", "claude"

  `description`:

  * Must be non-empty
  * Maximum 1,024 characters
  * Cannot contain XML tags
  * Should describe what the Skill does and when to use it

  For complete Skill structure details, see the [Skills overview](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview#skill-structure).
</Note>

### Naming conventions

Use consistent naming patterns to make Skills easier to reference and discuss. Consider using **gerund form** (verb + -ing) for Skill names, as this clearly describes the activity or capability the Skill provides.

Remember that the `name` field must use lowercase letters, numbers, and hyphens only.

**Good naming examples (gerund form):**

* `processing-pdfs`
* `analyzing-spreadsheets`
* `managing-databases`
* `testing-code`
* `writing-documentation`

**Acceptable alternatives:**

* Noun phrases: `pdf-processing`, `spreadsheet-analysis`
* Action-oriented: `process-pdfs`, `analyze-spreadsheets`

**Avoid:**

* Vague names: `helper`, `utils`, `tools`
* Overly generic: `documents`, `data`, `files`
* Reserved words: `anthropic-helper`, `claude-tools`
* Inconsistent patterns within your skill collection

Consistent naming makes it easier to:

* Reference Skills in documentation and conversations
* Understand what a Skill does at a glance
* Organize and search through multiple Skills
* Maintain a professional, cohesive skill library

### Writing effective descriptions

The `description` field enables Skill discovery and should include both what the Skill does and when to use it.

<Warning>
  **Always write in third person**. The description is injected into the system prompt, and inconsistent point-of-view can cause discovery problems.

  * **Good:** "Processes Excel files and generates reports"
  * **Avoid:** "I can help you process Excel files"
  * **Avoid:** "You can use this to process Excel files"
</Warning>

**Be specific and include key terms**. Include both what the Skill does and specific triggers/contexts for when to use it.

Each Skill has exactly one description field. The description is critical for skill selection: Claude uses it to choose the right Skill from potentially 100+ available Skills. Your description must provide enough detail for Claude to know when to select this Skill, while the rest of SKILL.md provides the implementation details.

Effective examples:

**PDF Processing skill:**

**Excel Analysis skill:**

**Git Commit Helper skill:**

Avoid vague descriptions like these:

### Progressive disclosure patterns

SKILL.md serves as an overview that points Claude to detailed materials as needed, like a table of contents in an onboarding guide. For an explanation of how progressive disclosure works, see [How Skills work](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview#how-skills-work) in the overview.

**Practical guidance:**

* Keep SKILL.md body under 500 lines for optimal performance
* Split content into separate files when approaching this limit
* Use the following patterns to organize instructions, code, and resources effectively

#### Visual overview: From simple to complex

A basic Skill starts with just a SKILL.md file containing metadata and instructions:

![Simple SKILL.md file showing YAML frontmatter and markdown body](https://platform.claude.com/docs/images/agent-skills-simple-file.png)

As your Skill grows, you can bundle additional content that Claude loads only when needed:

![Bundling additional reference files like reference.md and forms.md.](https://platform.claude.com/docs/images/agent-skills-bundling-content.png)

The complete Skill directory structure might look like this:

* `pdf/`

  * `SKILL.md`: Main instructions (loaded when triggered)

  * `FORMS.md`: Form-filling guide (loaded as needed)

  * `reference.md`: API reference (loaded as needed)

  * `examples.md`: Usage examples (loaded as needed)

  * `scripts/`

    * `analyze_form.py`: Utility script (executed, not loaded)
    * `fill_form.py`: Form filling script
    * `validate.py`: Validation script

#### Pattern 1: High-level guide with references

````markdown
---
name: pdf-processing
description: Extracts text and tables from PDF files, fills forms, and merges documents. Use when working with PDF files or when the user mentions PDFs, forms, or document extraction.
---

# PDF Processing


## Quick start

Source: https://platform.claude.com/llms-full.txt#quick-start-10

Extract text with pdfplumber:


## Advanced features

Source: https://platform.claude.com/llms-full.txt#advanced-features

**Form filling**: See [FORMS.md](FORMS.md) for complete guide
**API reference**: See [REFERENCE.md](REFERENCE.md) for all methods
**Examples**: See [EXAMPLES.md](EXAMPLES.md) for common patterns
`

`markdown SKILL.md
# BigQuery Data Analysis


## Available datasets

Source: https://platform.claude.com/llms-full.txt#available-datasets

**Finance**: Revenue, ARR, billing → See [reference/finance.md](reference/finance.md)
**Sales**: Opportunities, pipeline, accounts → See [reference/sales.md](reference/sales.md)
**Product**: API usage, features, adoption → See [reference/product.md](reference/product.md)
**Marketing**: Campaigns, attribution, email → See [reference/marketing.md](reference/marketing.md)


## Quick search

Source: https://platform.claude.com/llms-full.txt#quick-search

Find specific metrics using grep:

`

markdown
# DOCX Processing


## Creating documents

Source: https://platform.claude.com/llms-full.txt#creating-documents

Use docx-js for new documents. See [DOCX-JS.md](DOCX-JS.md).


## Editing documents

Source: https://platform.claude.com/llms-full.txt#editing-documents

For simple edits, modify the XML directly.

**For tracked changes**: See [REDLINING.md](REDLINING.md)
**For OOXML details**: See [OOXML.md](OOXML.md)

markdown
# SKILL.md
See [advanced.md](advanced.md)...

# advanced.md
See [details.md](details.md)...

# details.md
Here's the actual information...

markdown
# SKILL.md

**Basic usage**: [instructions in SKILL.md]
**Advanced features**: See [advanced.md](advanced.md)
**API reference**: See [reference.md](reference.md)
**Examples**: See [examples.md](examples.md)

markdown
# API Reference


## Contents

Source: https://platform.claude.com/llms-full.txt#contents

- Authentication and setup
- Core methods (create, read, update, delete)
- Advanced features (batch operations, webhooks)
- Error handling patterns
- Code examples


## Authentication and setup

Source: https://platform.claude.com/llms-full.txt#authentication-and-setup

...


## Core methods

Source: https://platform.claude.com/llms-full.txt#core-methods

...
```

Claude can then read the complete file or jump to specific sections as needed.

For details on how this filesystem-based architecture enables progressive disclosure, see the [Runtime environment](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices#runtime-environment) section later in this guide.


## Workflows and feedback loops

Source: https://platform.claude.com/llms-full.txt#workflows-and-feedback-loops

### Use workflows for complex tasks

Break complex operations into clear, sequential steps. For particularly complex workflows, provide a checklist that Claude can copy into its response and check off as it progresses.

**Example 1: Research synthesis workflow** (for Skills without code):

````markdown


## Research synthesis workflow

Source: https://platform.claude.com/llms-full.txt#research-synthesis-workflow

Copy this checklist and track your progress:

**Step 1: Read all source documents**

Review each document in the `sources/` directory. Note the main arguments and supporting evidence.

**Step 2: Identify key themes**

Look for patterns across sources. What themes appear repeatedly? Where do sources agree or disagree?

**Step 3: Cross-reference claims**

For each major claim, verify it appears in the source material. Note which source supports each point.

**Step 4: Create structured summary**

Organize findings by theme. Include:
- Main claim
- Supporting evidence from sources
- Conflicting viewpoints (if any)

**Step 5: Verify citations**

Check that every claim references the correct source document. If citations are incomplete, return to Step 3.
`

`markdown


## PDF form filling workflow

Source: https://platform.claude.com/llms-full.txt#pdf-form-filling-workflow

Copy this checklist and check off items as you complete them:

**Step 1: Analyze the form**

Run: `python scripts/analyze_form.py input.pdf`

This extracts form fields and their locations, saving to `fields.json`.

**Step 2: Create field mapping**

Edit `fields.json` to add values for each field.

**Step 3: Validate mapping**

Run: `python scripts/validate_fields.py fields.json`

Fix any validation errors before continuing.

**Step 4: Fill the form**

Run: `python scripts/fill_form.py input.pdf fields.json output.pdf`

**Step 5: Verify output**

Run: `python scripts/verify_output.py output.pdf`

If verification fails, return to Step 2.
`

markdown


## Content review process

Source: https://platform.claude.com/llms-full.txt#content-review-process

1. Draft your content following the guidelines in STYLE_GUIDE.md
2. Review against the checklist:
   - Check terminology consistency
   - Verify examples follow the standard format
   - Confirm all required sections are present
3. If issues found:
   - Note each issue with specific section reference
   - Revise the content
   - Review the checklist again
4. Only proceed when all requirements are met
5. Finalize and save the document

markdown


## Document editing process

Source: https://platform.claude.com/llms-full.txt#document-editing-process

1. Make your edits to `word/document.xml`
2. **Validate immediately**: `python ooxml/scripts/validate.py unpacked_dir/`
3. If validation fails:
   - Review the error message carefully
   - Fix the issues in the XML
   - Run validation again
4. **Only proceed when validation passes**
5. Rebuild: `python ooxml/scripts/pack.py unpacked_dir/ output.docx`
6. Test the output document
```

The validation loop catches errors early.


## Content guidelines

Source: https://platform.claude.com/llms-full.txt#content-guidelines

### Avoid time-sensitive information

Don't include information that will become outdated:

**Bad example: Time-sensitive** (will become wrong):

**Good example** (use "old patterns" section):

```markdown


## Current method

Source: https://platform.claude.com/llms-full.txt#current-method

Use the v2 API endpoint: `api.example.com/v2/messages`
