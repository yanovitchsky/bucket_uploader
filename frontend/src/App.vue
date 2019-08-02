<template>
  <a-layout id="app">
    <Header>
      <a-menu mode='horizontal'>
        <a-menu-item>Buckets</a-menu-item>
        <a-menu-item>Jobs</a-menu-item>
      </a-menu>
    </Header>
    <Content class='content'>
      <router-view/>
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
</style>
