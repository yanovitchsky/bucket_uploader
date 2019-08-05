<template>
  <div class="bucket-list">
    <div v-if="buckets.length > 0">
      <div class="add-bucket">
        <a-button type="primary" @click="newBucket">Add a bucket</a-button>
      </div>
      <a-list
        size="large"
        bordered
        :dataSource="buckets"
      >
        <a-list-item slot="renderItem" slot-scope="item, index">
          <a slot="actions" v-if="item.deletable" @click="deleteBucket(item.id)"><a-icon type="delete" /></a>
          <div>
            <img src="@/assets/s3.jpg" alt="" width="40" height="30" v-if="item.bucket_type == 'Amazon S3'">
            <img src="@/assets/gcs.jpg" alt="" width="40" height="30" v-else>
            {{item.name}}
          </div>
        </a-list-item>
      </a-list>
    </div>
    <div v-else>
      <div class="empty-bucket">You do not have any bucket.</div>
      <div class="add-bucket">
        <a-button type="primary" @click="newBucket">Add a bucket</a-button>
      </div>
    </div>
  </div>
</template>
<script>
import axios from 'axios'

import '../../assets/logo.png'

export default {
  data () {
    return {
      buckets: []
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
    newBucket () {
      this.$router.push('/buckets/new')
    },
    async deleteBucket (id) {
      const path = `http://localhost:5000/api/buckets/${id}`
      try {
        await axios.delete(path)
        let newBuckets = this.buckets.filter(b => b.id !== id)
        this.buckets = newBuckets
      } catch (error) {
        console.log('error', error)
      }
    }
  },
  mounted () {
    this.getBuckets()
  }
}
</script>
<style scoped>
.bucket-list {
  width: 100%;
}
.add-bucket {
  padding-bottom: 10px;
  padding-top: 10px;
}
.empty-bucket {
  font-size: 1rem;
}
</style>

