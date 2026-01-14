<script setup lang="ts">
import { RouterView } from 'vue-router'
import Navbar from './components/Navbar.vue'
</script>

<template>
  <Navbar class="navbar-root" />
  <RouterView class="router-root" />
</template>

<style>
@import 'assets/sizes.css';
@import 'assets/colors.css';

#app {
  padding-top: var(--navbar-height);
}

.navbar-root {
  width: var(--navbar-width);
}

.router-root {
  min-height: var(--main-content-height);
  width: var(--main-content-width);
  background-color: var(--color-background-primary);
}
</style>
