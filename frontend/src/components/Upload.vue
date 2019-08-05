<template>
  <div class="root-div">
    <div class="b-select">
      <a-select 
      placeholder="Select a google storage bucket" 
      @change="handleChange"
      showSearch
      optionFilterProp="children"
      style="width: 400px"
      :filterOption="filterOption"
      >
        <a-select-option v-for="bucket in buckets" :key="bucket.id" :value="bucket.name">{{bucket.name}}</a-select-option>
      </a-select>
    </div>
    <div class='b-upload'>
      <a-upload
        :fileList="fileList"
        :remove="handleRemove"
        :beforeUpload="beforeUpload"
        :multiple="true"
      >
        <a-button>
          <a-icon type="upload" /> Select File
        </a-button>
      </a-upload>
      <a-button
        type="primary"
        @click="handleUpload"
        :disabled="fileList.length === 0 || selectedBucket === null"
        :loading="uploading"
        style="margin-top: 16px"
      >
        {{uploading ? 'Uploading' : 'Start Upload' }}
      </a-button>

    </div>
  </div>
</template>
<script>
import axios from 'axios'
export default {
  data () {
    return {
      buckets: [],
      fileList: [],
      uploading: false,
      selectedBucket: null
    }
  },
  methods: {
    handleChange (value) {
      console.log(`selected ${value}`)
      const choosen = this.buckets.find(bucket => bucket.name === value)
      this.selectedBucket = choosen
    },
    filterOption (input, option) {
      return option.componentOptions.children[0].text.toLowerCase().indexOf(input.toLowerCase()) >= 0
    },
    handleRemove (file) {
      const index = this.fileList.indexOf(file)
      const newFileList = this.fileList.slice()
      newFileList.splice(index, 1)
      this.fileList = newFileList
    },
    beforeUpload (file) {
      this.fileList = [...this.fileList, file]
      return false
    },
    async handleUpload () {
      const { fileList } = this
      const formData = new FormData()
      fileList.forEach((file) => {
        formData.append('files', file)
      })
      formData.append('bucket_id', this.selectedBucket.id)
      this.uploading = true
      try {
        const path = '/api/upload'
        await axios.post(path, formData, {headers: {'Content-Type': 'multipart/form-data'}})
        this.fileList = []
        this.uploading = false
        this.$message.success('upload successfully.')
      } catch (error) {
        this.uploading = false
        this.$message.error('upload failed.')
        console.log('error', error)
      }
    },
    async getBuckets () {
      try {
        const path = `/api/buckets`
        const response = await axios.get(path)
        this.buckets = response.data.buckets.filter(bucket => bucket.bucket_type === 'Google Storage')
      } catch (error) {
        console.log('error', error)
        this.$message.error('cannot get buckets')
      }
    }
  },
  mounted () {
    this.getBuckets()
  }
}
</script>
<style scoped>
.root-div {
  width: 100%;
}
.b-select {
  padding-bottom: 20px;
}
</style>
