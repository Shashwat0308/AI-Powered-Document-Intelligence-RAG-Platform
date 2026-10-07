const API_BASE_URL = "http://127.0.0.1:8000";


/* =========================
   AUTHENTICATION
========================= */

function getAuthHeaders(includeJSON = false) {

    const token =
        localStorage.getItem("documind_token");

    const headers = {};

    if (includeJSON) {

        headers["Content-Type"] =
            "application/json";
    }

    if (token) {

        headers["Authorization"] =
            `Bearer ${token}`;
    }

    return headers;
}


function handleUnauthorized() {

    localStorage.removeItem(
        "documind_token"
    );

    localStorage.removeItem(
        "documind_user"
    );

    alert(
        "Your session has expired. Please login again."
    );

    window.location.href =
        "login.html";
}


/* =========================
   ELEMENTS
========================= */

const fileInput =
    document.getElementById("fileInput");

const uploadBtn =
    document.getElementById("uploadBtn");

const documentList =
    document.getElementById("documentList");

const documentCount =
    document.getElementById("documentCount");

const sidebarDocumentCount =
    document.getElementById("sidebarDocumentCount");

const questionInput =
    document.getElementById("questionInput");

const askBtn =
    document.getElementById("askBtn");

const messages =
    document.getElementById("messages");

const welcomeMessage =
    document.getElementById("welcomeMessage");

const statusMessage =
    document.getElementById("statusMessage");

const themeBtn =
    document.getElementById("themeBtn");

const mobileMenuBtn =
    document.getElementById("mobileMenuBtn");

const sidebar =
    document.getElementById("sidebar");


/* =========================
   STATUS
========================= */

function setStatus(message) {

    if (statusMessage) {

        statusMessage.textContent =
            message;
    }
}


/* =========================
   THEME SYSTEM
========================= */

function applyTheme() {

    const savedTheme =
        localStorage.getItem(
            "documind-app-theme"
        );

    if (savedTheme) {

        document.documentElement.setAttribute(
            "data-theme",
            savedTheme
        );

        updateThemeIcon(savedTheme);

        return;
    }

    const prefersDark =
        window
            .matchMedia(
                "(prefers-color-scheme: dark)"
            )
            .matches;

    const theme =
        prefersDark
            ? "dark"
            : "light";

    document.documentElement.setAttribute(
        "data-theme",
        theme
    );

    updateThemeIcon(theme);
}


function toggleTheme() {

    const currentTheme =
        document.documentElement.getAttribute(
            "data-theme"
        );

    const newTheme =
        currentTheme === "dark"
            ? "light"
            : "dark";

    document.documentElement.setAttribute(
        "data-theme",
        newTheme
    );

    localStorage.setItem(
        "documind-app-theme",
        newTheme
    );

    updateThemeIcon(newTheme);
}


function updateThemeIcon(theme) {

    if (!themeBtn) return;

    themeBtn.textContent =
        theme === "dark"
            ? "☀"
            : "☾";

    themeBtn.title =
        theme === "dark"
            ? "Switch to light mode"
            : "Switch to dark mode";
}


if (themeBtn) {

    themeBtn.addEventListener(
        "click",
        toggleTheme
    );
}


applyTheme();


/* =========================
   MOBILE SIDEBAR
========================= */

if (mobileMenuBtn) {

    mobileMenuBtn.addEventListener(
        "click",
        () => {

            sidebar.classList.toggle(
                "open"
            );

        }
    );
}


/* Close sidebar when clicking
   outside it on mobile */

document.addEventListener(
    "click",
    (event) => {

        if (
            window.innerWidth <= 720 &&
            sidebar &&
            sidebar.classList.contains("open") &&
            !sidebar.contains(event.target) &&
            mobileMenuBtn &&
            !mobileMenuBtn.contains(event.target)
        ) {

            sidebar.classList.remove(
                "open"
            );

        }

    }
);


/* Close sidebar after selecting
   a navigation item on mobile */

document
    .querySelectorAll(".nav-item")
    .forEach(button => {

        button.addEventListener(
            "click",
            () => {

                if (
                    window.innerWidth <= 720 &&
                    sidebar
                ) {

                    sidebar.classList.remove(
                        "open"
                    );

                }

            }
        );

    });


/* =========================
   DOCUMENT LIST
========================= */

function addDocumentToList(documentData) {

    const emptyText =
        document.querySelector(
            ".empty-text"
        );

    if (emptyText) {

        emptyText.remove();
    }


    /*
     * Backend now returns document objects:
     *
     * {
     *     id,
     *     filename,
     *     file_size,
     *     page_count,
     *     chunk_count,
     *     uploaded_at
     * }
     *
     * Keep compatibility with a plain filename too.
     */

    const filename =
        typeof documentData === "string"
            ? documentData
            : documentData.filename;


    if (!filename) return;


    const item =
        document.createElement("div");

    item.className =
        "document-item";


    item.innerHTML = `
        <span>📄</span>

        <span title="${escapeHTML(filename)}">
            ${escapeHTML(filename)}
        </span>
    `;


    documentList.appendChild(item);


    const count =
        documentList.querySelectorAll(
            ".document-item"
        ).length;


    if (documentCount) {

        documentCount.textContent =
            count;
    }


    if (sidebarDocumentCount) {

        sidebarDocumentCount.textContent =
            count;
    }
}


/* =========================
   UPLOAD DOCUMENT
========================= */

if (uploadBtn) {

    uploadBtn.addEventListener(
        "click",
        async () => {

            const file =
                fileInput.files[0];


            if (!file) {

                setStatus(
                    "Please select a document first."
                );

                return;
            }


            uploadBtn.disabled = true;

            uploadBtn.textContent =
                "Uploading...";

            setStatus(
                "Processing document..."
            );


            const formData =
                new FormData();


            formData.append(
                "file",
                file
            );


            try {

                const response =
                    await fetch(
                        `${API_BASE_URL}/documents/upload`,
                        {
                            method: "POST",

                            headers:
                                getAuthHeaders(),

                            body: formData
                        }
                    );


                if (response.status === 401) {

                    handleUnauthorized();

                    return;
                }


                const data =
                    await response.json();


                if (!response.ok) {

                    throw new Error(
                        data.detail ||
                        "Upload failed."
                    );
                }


                console.log(
                    "Upload response:",
                    data
                );


                /*
                 * Refresh the complete document list
                 * from PostgreSQL/backend.
                 */

                await loadDocuments();


                setStatus(
                    "Document indexed successfully."
                );


                fileInput.value = "";


            } catch (error) {

                console.error(
                    "Upload error:",
                    error
                );


                setStatus(
                    error.message ||
                    "Could not upload document."
                );


            } finally {

                uploadBtn.disabled =
                    false;

                uploadBtn.textContent =
                    "Upload Document";
            }

        }
    );

}


/* =========================
   ASK QUESTION
========================= */

if (askBtn) {

    askBtn.addEventListener(
        "click",
        askQuestion
    );
}


if (questionInput) {

    questionInput.addEventListener(
        "keydown",
        (event) => {

            if (
                event.key === "Enter" &&
                !event.shiftKey
            ) {

                event.preventDefault();

                askQuestion();
            }

        }
    );

}


async function askQuestion() {

    const question =
        questionInput.value.trim();


    if (!question) {

        setStatus(
            "Please enter a question."
        );

        return;
    }


    welcomeMessage.style.display =
        "none";


    addUserMessage(question);


    questionInput.value = "";


    askBtn.disabled = true;


    setStatus(
        "Searching your documents..."
    );


    try {

        const response =
            await fetch(
                `${API_BASE_URL}/ask`,
                {
                    method: "POST",

                    headers:
                        getAuthHeaders(true),

                    body: JSON.stringify({
                        question: question
                    })
                }
            );


        if (response.status === 401) {

            handleUnauthorized();

            return;
        }


        const data =
            await response.json();


        if (!response.ok) {

            throw new Error(
                data.detail ||
                "Question request failed."
            );
        }


        console.log(
            "RAG response:",
            data
        );


        addAIMessage(
            data.answer ||
            "No answer was returned.",
            data.sources || []
        );


        setStatus("");


    } catch (error) {

        console.error(error);


        addAIMessage(
            "I couldn't connect to the RAG backend. Please make sure FastAPI is running.",
            []
        );


        setStatus(
            "Backend connection failed."
        );


    } finally {

        askBtn.disabled =
            false;
    }
}


/* =========================
   USER MESSAGE
========================= */

function addUserMessage(text) {

    const message =
        document.createElement("div");


    message.className =
        "message message-user";


    message.innerHTML = `
        <div class="user-bubble">
            ${escapeHTML(text)}
        </div>
    `;


    messages.appendChild(message);


    scrollToBottom();
}


/* =========================
   AI MESSAGE
========================= */

function addAIMessage(
    answer,
    sources
) {

    const message =
        document.createElement("div");


    message.className =
        "message ai-message";


    let sourcesHTML = "";


    if (sources.length > 0) {

        sourcesHTML = `
            <div class="sources">

                ${sources.map(
                    source => {

                        const filename =
                            source.filename ||
                            source.file ||
                            source.document ||
                            source.source ||
                            "Document";


                        const page =
                            source.page ||
                            source.page_number ||
                            "Unknown";


                        return `
                            <div class="source">
                                📑
                                ${escapeHTML(
                                    String(filename)
                                )}
                                — Page
                                ${escapeHTML(
                                    String(page)
                                )}
                            </div>
                        `;

                    }
                ).join("")}

            </div>
        `;
    }


    message.innerHTML = `
        <div class="ai-icon">
            AI
        </div>

        <div class="ai-content">

            <div>
                ${formatAnswer(answer)}
            </div>

            ${sourcesHTML}

        </div>
    `;


    messages.appendChild(message);


    scrollToBottom();
}


/* =========================
   ANSWER FORMATTING
========================= */

function formatAnswer(text) {

    return escapeHTML(
        String(text)
    ).replace(
        /\n/g,
        "<br>"
    );
}


/* =========================
   SECURITY
========================= */

function escapeHTML(text) {

    const div =
        document.createElement("div");


    div.textContent =
        text;


    return div.innerHTML;
}


/* =========================
   SCROLL
========================= */

function scrollToBottom() {

    messages.scrollTop =
        messages.scrollHeight;
}


/* =========================
   LOAD EXISTING DOCUMENTS
========================= */

async function loadDocuments() {

    try {

        const response =
            await fetch(
                `${API_BASE_URL}/documents`,
                {
                    method: "GET",

                    headers:
                        getAuthHeaders()
                }
            );


        if (response.status === 401) {

            handleUnauthorized();

            return;
        }


        const data =
            await response.json();


        if (!response.ok) {

            throw new Error(
                data.detail ||
                "Could not load documents."
            );
        }


        documentList.innerHTML = "";


        if (
            !data.documents ||
            data.documents.length === 0
        ) {

            documentList.innerHTML = `
                <p class="empty-text">
                    No documents indexed yet.
                </p>
            `;


            documentCount.textContent =
                "0";


            if (sidebarDocumentCount) {

                sidebarDocumentCount.textContent =
                    "0";
            }


            return;
        }


        /*
         * Backend returns objects now,
         * so pass the entire document object.
         */

        data.documents.forEach(
            documentData => {

                addDocumentToList(
                    documentData
                );

            }
        );


    } catch (error) {

        console.error(
            "Document loading error:",
            error
        );

    }
}


/* =========================
   LOAD DOCUMENTS
========================= */

loadDocuments();