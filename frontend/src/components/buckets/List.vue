<template>
  <div>
    <div v-if="buckets.length > 0">
      
    </div>
    <div v-else>
      You do not have any bucket.
      <a-button type="primary" @click="showModal">Add a bucket</a-button>
    </div>
    <a-modal
      title="Add a bucket"
      :visible="visible"
      @ok="handleOk"
      @cancel="handleCancel"
    >
      <new-bucket />
    </a-modal>
  </div>
</template>
<script>
import axios from 'axios'
import Create from '../buckets/Create'
export default {
  components: {
    'new-bucket': Create
  },
  data () {
    return {
      buckets: [],
      visible: false
    }
  },
  methods: {
    getBuckets () {
      const path = `http://localhost:5000/api/buckets`
      axios.get(path)
      .then(response => {
        this.buckets = response.data.buckets
      })
      .catch(error => {
        console.log(error)
      })
    },
    showModal () {
      this.visible = true
    },
    handleOk (e) {

    },
    handleCancel (e) {
      this.visible = false
    }
  }
}
</script>
