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
import io.ktor.client.engine.okhttp.*
import io.ktor.client.request.*
import io.ktor.client.statement.*
import kotlinx.coroutines.launch
import kotlinx.coroutines.runBlocking
import org.jetbrains.compose.ui.tooling.preview.Preview

val client = HttpClient(OkHttp)

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
                            val jwt: String = client.request("https://ktor.io/").bodyAsText()
                            navigator.push(ChatScreen(jwt))
                        }
                    }
                }) {
                    Text("Login")
                }
            }
        }
    }
}

class ChatScreen(private val jwt: String):Screen {
    private val randomValue: String
        get() = "a"

    @Composable
    @Preview
    override fun Content() {
        var msg: String by remember { mutableStateOf("") }
        val stateStack = rememberStateStack<String>()
        val (selectedItem, selectItem) = rememberSaveable { mutableStateOf("") }

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
                    stateStack.push(msg)
                    println(stateStack)
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