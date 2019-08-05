<template>
  <div class="root-div">
    <div>
      <p>
        Select the source bucket and the destination bucket.
        If you do not specify which file to transfer, the whole bucket will be transfered to the destination.
      </p>
    </div>
    <div class="source-select">
      <a-select 
      placeholder="Source Bucket" 
      @change="handleSourceChange"
      showSearch
      optionFilterProp="children"
      style="width: 400px"
      :filterOption="filterOption"
      >
        <a-select-option v-for="bucket in sources" :key="bucket.id" :value="bucket.id">{{bucket | withType}}</a-select-option>
      </a-select>
    </div>
    <div class="b-files" v-if="sourceFiles.length > 0">
      <a-table 
        :columns="columns" 
        :dataSource="humanSourceFiles" 
        :pagination="{ pageSize: 50 }" 
        :scroll="{ y: 240 }"  
        :rowSelection="{onChange: onSelectChange}"
        :rowKey="record => record.name"/>
    </div>
    <div class="sink-select">
      <a-select 
      placeholder="Destination Bucket" 
      @change="handleSinkChange"
      showSearch
      optionFilterProp="children"
      style="width: 400px"
      :filterOption="filterOption"
      >
        <a-select-option v-for="bucket in sinks" :key="bucket.id" :value="bucket.id">{{bucket | withType}}</a-select-option>
      </a-select>
    </div>
    <div class="add-bucket">
        <a-button type="primary" @click="createTransfer">Start Transfer</a-button>
      </div>
  </div>
</template>
<script>
import axios from 'axios'
import bytes from 'bytes'
const columns = [
  {
    title: 'Name',
    dataIndex: 'name',
    width: 150
  },
  {
    title: 'Size',
    dataIndex: 'size',
    width: 150
  }
]
export default {
  data () {
    return {
      buckets: [],
      source: {id: -1},
      sink: {id: -1},
      sourceFiles: [],
      selectedFiles: [],
      columns
    }
  },
  methods: {
    async getBuckets () {
      try {
        const path = `http://localhost:5000/api/buckets`
        const response = await axios.get(path)
        this.buckets = response.data.buckets
      } catch (error) {
        console.log('error', error)
        this.$message.error('cannot get buckets')
      }
    },
    filterOption (input, option) {
      return option.componentOptions.children[0].text.toLowerCase().indexOf(input.toLowerCase()) >= 0
    },
    handleSourceChange (value) {
      console.log(`selected ${value}`)
      this.source = this.buckets.find(bucket => bucket.id === value)
      this.getFiles(value)
    },
    handleSinkChange (value) {
      console.log(`selected ${value}`)
      this.sink = this.buckets.find(bucket => bucket.id === value)
    },
    async createTransfer () {
      try {
        const path = `http://localhost:5000/api/transfers`
        const files = this.selectedFiles.map(x => x.name)
        const params = {
          sourceId: this.source.id,
          sinkId: this.sink.id,
          files: files
        }
        await axios.post(path, params)
        this.$router.push('/transfers')
      } catch (error) {
        console.log(error)
        this.$message.error('Cannot create transfer')
      }
    },
    async getFiles (bucketId) {
      try {
        const path = `http://localhost:5000/api/buckets/${bucketId}/files`
        const response = await axios.get(path)
        this.sourceFiles = response.data.files
      } catch (error) {
        console.log(error)
        const bucket = this.buckets.find(b => b.id === bucketId)
        this.$message.error(`cannot get files for bucket ${bucket.name}`)
        this.sourceFiles = []
      }
    },
    onSelectChange (_selectedRowKeys, selectedRows) {
      this.selectedFiles = selectedRows
    }
  },
  computed: {
    sources () {
      return this.buckets.filter(bucket => bucket.id !== this.sink.id)
    },
    sinks () {
      return this.buckets
      .filter(bucket => bucket.bucket_type === 'Google Storage')
      .filter(bucket => bucket.id !== this.source.id)
    },
    humanSourceFiles () {
      return this.sourceFiles.map(f => {
        return {
          name: f.name,
          size: bytes(f.size)
        }
      })
    }
  },
  filters: {
    withType (bucket) {
      const type = bucket.bucket_type === 'Amazon S3' ? 'S3' : 'GCS'
      return `${bucket.name} (${type})`
    }
  },
  mounted () {
    this.getBuckets()
  }
}
</script>
<style scoped>
.root-div {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  height: 600px;
}
</style>
