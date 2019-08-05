<template>
  <a-layout id="app">
    <Header>
      <a-menu mode='horizontal'>
        <a-menu-item>
          <router-link to='/'>Buckets</router-link>
        </a-menu-item>
        <a-menu-item>
          <router-link to='/transfers'>Transfers</router-link>
        </a-menu-item>
        <a-menu-item>
          <router-link to="/uploads">Uploads</router-link>
        </a-menu-item>
      </a-menu>
    </Header>
    <Content class='content'>
      <a-row>
        <a-col :span="24">
          <router-view class='content-inside'/>
        </a-col>
      </a-row>
    </Content>
    <Footer></Footer>
  </a-layout>
</template>

<script>

export default {
  name: 'app'
}
</script>

<style>
#app {
  font-family: 'Avenir', Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  /* text-align: center; */
  color: #2c3e50;
  background-color: white;
  /* margin-top: 60px; */
}

.content {
  padding: 0 50px;
  margin-top: 64px;
  min-height: 380px;
  text-align: center;
}
.content-inside {
  display: inline-block
}
</style>
