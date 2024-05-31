import androidx.compose.animation.AnimatedVisibility
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.RowScope
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.LazyItemScope
import androidx.compose.foundation.lazy.itemsIndexed
import androidx.compose.material.Button
import androidx.compose.material.MaterialTheme
import androidx.compose.material.Text
import androidx.compose.material.TextField
import androidx.compose.runtime.*
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.ui.Alignment
import androidx.compose.foundation.lazy.items
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import cafe.adriel.voyager.core.screen.Screen
import cafe.adriel.voyager.core.stack.rememberStateStack
import cafe.adriel.voyager.navigator.LocalNavigator
import cafe.adriel.voyager.navigator.Navigator
import cafe.adriel.voyager.navigator.currentOrThrow
import cafe.adriel.voyager.transitions.SlideTransition
import io.ktor.client.*
import io.ktor.client.call.body
import io.ktor.client.call.receive
import io.ktor.client.request.*
import io.ktor.client.statement.*
import io.ktor.http.*
import io.ktor.client.engine.okhttp.*
import io.ktor.client.plugins.auth.*
import io.ktor.serialization.kotlinx.json.*
import kotlinx.serialization.Serializable
import kotlinx.serialization.json.Json
import io.ktor.client.plugins.auth.providers.BearerTokens
import io.ktor.client.plugins.auth.providers.bearer
import io.ktor.client.plugins.contentnegotiation.ContentNegotiation
import io.ktor.client.request.forms.submitForm
import io.ktor.serialization.kotlinx.json.json
import kotlinx.coroutines.launch
import kotlinx.coroutines.runBlocking
import org.jetbrains.compose.ui.tooling.preview.Preview



val client = HttpClient(OkHttp) {
    install(ContentNegotiation) {
        json(Json {
            ignoreUnknownKeys = true
            isLenient = true
        })
    }
}

@Composable
@Preview
fun App() {
    MaterialTheme {
        Navigator(screen = AuthScreen()) {
            navigator -> SlideTransition(navigator)
        }
    }
}

class AuthScreen():Screen {
    @Composable
    @Preview
    override fun Content() {
        val navigator = LocalNavigator.currentOrThrow

        var username: String by remember { mutableStateOf("") }
        var password: String by remember { mutableStateOf("") }
        Column(Modifier.fillMaxWidth(), horizontalAlignment = Alignment.CenterHorizontally) {
            Spacer(modifier = Modifier.height(8.dp))
            TextField(
                value = username,
                onValueChange = { username = it }
            )
            Spacer(modifier = Modifier.height(8.dp))
            TextField(
                value = password,
                onValueChange = { password = it }
            )
            Spacer(modifier = Modifier.height(8.dp))
            AnimatedVisibility(username.isNotEmpty() && password.isNotEmpty()) {
                Button(onClick = {
                    runBlocking {
                        launch {
                            val response: HttpResponse = client.submitForm (
                                url = "http://127.0.0.1:8000/token",
                                formParameters = Parameters.build {
                                    append("grant_type", "")
                                    append("username", username)
                                    append("password", password)
                                    append("scope", "")
                                    append("client_id", "")
                                    append("client_secret", "")
                                },
                                encodeInQuery = false
                            ) {
                                headers {
                                    append(HttpHeaders.Accept, "application/json")
                                    append(HttpHeaders.ContentType, "application/x-www-form-urlencoded")
                                }
                            }

                            val jwt: TokenResponseAPI = response.body()

                            navigator.push(ChatScreen(jwt.access_token))
                        }
                    }
                }) {
                    Text("Login")
                }
            }
            AnimatedVisibility(username.isNotEmpty() && password.isNotEmpty()) {
                Button(onClick = {
                    runBlocking {
                        launch {
                            val param = parameters {
                                append("username", username)
                                append("password", password)
                            }.formUrlEncode()
                            val response = client.post(
                                urlString = "http://127.0.0.1:8000/user/register?$param"
                            )  {
                                headers {
                                    append(HttpHeaders.Accept, "application/json")
                                }
                            }
                            username = ""
                            password = ""
                        }
                    }
                }) {
                    Text("Register")
                }
            }
        }
    }
}

class ChatScreen(private val jwt: String):Screen {

    @Composable
    @Preview
    override fun Content() {
        var msg: String by remember { mutableStateOf("") }
        val stateStack = rememberStateStack<String>()
        var user: UserAPI? by remember { mutableStateOf(null) }
        var nmessages: Int? by remember { mutableStateOf(null) }
        var message: MessageAPI? by remember { mutableStateOf(null) }

        if (user == null){
            runBlocking {
                launch {
                    val response = client.get(
                        urlString = "http://127.0.0.1:8000/user"
                    ) {
                        headers {
                            append(HttpHeaders.Accept, "application/json")
                            append(HttpHeaders.Authorization, "Bearer $jwt")
                        }
                    }
                    user = response.body()
                    println(user)
                }
            }
        }
        if (nmessages == null && user != null) {
            runBlocking {
                launch {
                    val response = client.get(
                        urlString = "http://127.0.0.1:8000/chat/number"
                    ) {
                        headers {
                            append(HttpHeaders.Accept, "application/json")
                            append(HttpHeaders.Authorization, "Bearer $jwt")
                        }
                    }
                    nmessages = response.body()
                }
            }
        }

        if (nmessages != null && user != null) {
            for (i in 0 until nmessages!!) {
                runBlocking {
                    launch {
                        val response = client.get(
                            urlString = "http://127.0.0.1:8000/chat/message/$i"
                        ) {
                            headers {
                                append(HttpHeaders.Accept, "application/json")
                                append(HttpHeaders.Authorization, "Bearer $jwt")
                            }
                        }
                        message = response.body()
                        if (message?.sender == "user") {
                            stateStack.push("${user?.username}: ${message?.content}")
                        } else {
                            stateStack.push("${message?.sender}: ${message?.content}")
                        }
                    }
                }
            }
            nmessages = -1 // Halt
        }

        Column {
            LazyColumn(
                contentPadding = PaddingValues(16.dp),
                reverseLayout = true,
                modifier = Modifier.weight(.8f)
            ) {
                itemsIndexed(
                    stateStack.items
                ) { index, item ->
                    Text(stateStack.items.reversed().get(index))
                }
                if (stateStack.isEmpty) {
                    item {
                        Text(
                            text = "EMPTY",
                            textAlign = TextAlign.Center,
                            color = Color.DarkGray,
                            fontWeight = FontWeight.Normal,
                            fontFamily = FontFamily.Monospace,
                            modifier = Modifier.fillMaxWidth()
                        )
                    }
                }
            }
            Row(
                modifier = Modifier.weight(.1f)
            ) {
                TextField(
                    value = msg,
                    onValueChange = { msg = it },
                    modifier = Modifier.fillMaxWidth()
                )
            }
            Row(
                modifier = Modifier.weight(.1f)
            ) {
                ActionButton(text = "Send") {
                    stateStack.push("${user?.username}: ${msg}")
                    runBlocking {
                        launch {
                            val param = parameters { append("message", msg) }.formUrlEncode()
                            val response = client.get(
                                urlString = "http://127.0.0.1:8000/chat/send?$param"
                            ) {
                                headers {
                                    append(HttpHeaders.Accept, "application/json")
                                    append(HttpHeaders.Authorization, "Bearer $jwt")
                                }
                            }
                            val tmpmsg: String = response.body()
                            stateStack.push("assistant: $tmpmsg")
                        }
                    }
                    msg = ""
                }
            }
        }
    }

    @Composable
    private fun RowScope.ActionButton(
        text: String,
        enabled: Boolean = true,
        onClick: () -> Unit
    ) {
        Button(
            onClick = onClick,
            enabled = enabled,
            modifier = Modifier
                .weight(.1f)
                .padding(8.dp)
        ) {
            Text(text = text)
        }
    }
}

@Serializable
data class TokenResponseAPI(val access_token: String, val token_type: String)

@Serializable
data class UserAPI(val id: Int, val username: String)

@Serializable
data class MessageAPI(val sender: String, val content: String, val order: Int)
