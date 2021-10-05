marked.use({ headerIds: false })

const Home = {
    data() {
        return {
            greeting:
                ['hi', 'hey', 'hello'][(Math.random() * 3) | 0] +
                ' ' +
                [':D', ':O'][(Math.random() * 2) | 0]
        }
    },
    template: `
    <h1>{{ greeting }}</h1>
    <p>
        <b id="welcome">{{ firstVisit? 'Welcome!' : 'Welcome back!' }}</b>
        this page aggregates info about <b>tetris-discord</b>, an
        almost-guideline-compliant tetris clone that runs on a discord bot!
    </p>
    <p v-if="firstVisit">
        If it's your first time hearing about this, check out these links!
    </p>
    <div id="links">
        <a
            rel="noreferrer noopener"
            target="_blank"
            href="https://discord.gg/ytJj3eQ74B"
        >
            Discord server
        </a>
        <a
            rel="noreferrer noopener"
            target="_blank"
            href="https://github.com/dzshn/tetris-discord"
        >
            Github repo
        </a>
        <a
            rel="noreferrer noopener"
            target="_blank"
            href="https://discord.com/api/oauth2/authorize?client_id=883520648553594920&permissions=116736&scope=bot%20applications.commands"
        >
            Bot invite
        </a>
        <a
            rel="noreferrer noopener"
            target="_blank"
            href="https://www.patreon.com/dzshn"
        >
            Patreon
        </a>
        <router-link to="/index" class="btn">View documentation</router-link>
        <router-link to="/changelog" class="btn">Changelog</router-link>
    </div>
    <Footer/>
    `,
    inject: ['repo', 'firstVisit']
}

const Index = {
    data() {
        return {
            index: [
                { title: 'Commands', page: 'commands' },
                { title: 'Quickstart', page: 'quickstart' }
            ]
        }
    },
    template: `
    <nav>
        <p>
            <li v-for="link in index">
                <router-link :to="'/docs/' + link.page">
                    {{ link.title }}
                </router-link>
            </li>
        </p>
    </nav>
    <router-link to="/" class="btn">Go back</router-link>
    <Footer/>
    `
}

const DocPage = {
    data() {
        return {
            content: '<h1 class="mono">Loading...</h1>'
        }
    },
    mounted() {
        fetch(`/pages/${this.$route.params.page}.md`).then(response => {
            if (response.status == 404) {
                this.$router.replace('/404')
                return
            }

            response.text().then(text => {
                this.content = marked(text)
            })
        })

        this.content
    },
    template: `<main v-html="content"></main><Footer/>`
}

const Changelog = {
    template: `
    <div>
        <p class="mono">
            <i>// TODO: this page.</i> <br> <br>

            (t:=__import__('iter'+'tool'+'s')),+(m:= <br>
            __import__('numpy').zeros((32,56),dtype= <br>
            int)),[((c:=(x+y*1j)/16-(2.5+1j)),(z:=0j <br>
            ),(i:=0),[*t.takewhile(lambda x:abs(z)<= <br>
            2,(((z:=z**2+c),(i:=i+1))for _ in range( <br>
            512)))],m.__setitem__((y,x),i))for (x,y) <br>
            in t.product(*map(range,reversed(m.shape <br>
            )))],print('\n'.join(''.join('█▓▒░ ░▒▓█' <br>
            [i%9]for i in j)for j in m)) <br> <br>
        </p>
    </div>
    <Footer/>`,
    inject: ['commits']
}

const NotFound = {
    mounted() {
        if (this.$route.path != '/404') this.$router.replace('/404')
    },
    template: `
    <h1>404!</h1>
    <p>Looks like that page doesn't exist... <br>
    Think it's an error? let us know in the discord server!</p> <br>
    <router-link to="/" class="btn">Go back to main page</router-link>
    <Footer/>
    `
}

const Footer = {
    template: `
    <footer>
        <i>Copyright (c) 2021 Sofia "dzshn" N. L.</i>
        <i>
            <a
                rel="noreferrer noopener"
                target="_blank"
                href="https://github.com/dzshn/tetris-discord/blob/main/LICENSE"
            >
                MIT License
            </a>
        </i>
    </footer>
    `
}

const router = VueRouter.createRouter({
    history: VueRouter.createHashHistory(),
    routes: [
        { path: '/', component: Home },
        { path: '/index', component: Index },
        { path: '/docs/:page', component: DocPage },
        { path: '/changelog', component: Changelog },
        { path: '/404', component: NotFound },
        { path: '/:_(.*)', component: NotFound }
    ]
})

const app = Vue.createApp({
    provide() {
        return {
            repo: {},
            commits: [],
            firstVisit: localStorage.getItem('firstVisit') == null
        }
    },
    mounted() {
        setTimeout(() => {
            localStorage.setItem('firstVisit', 'yes')
        }, 10000)
        /* fetch('https://api.github.com/repos/dzshn/tetris-discord').then(
            response => {
                console.assert(response.ok, 'Error fetching repo data')
                response.json().then(json => {
                    this.repo = json
                })
            }
        )
        fetch('https://api.github.com/repos/dzshn/tetris-discord/commits').then(
            response => {
                console.assert(response.ok, 'Error fetching repo commits')
                response.json().then(json => {
                    this.commits = json
                })
            }
        ) */
    }
})

app.use(router)
app.component('Footer', Footer)
app.mount('#app')
